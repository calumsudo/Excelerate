# managers/coordinator.py
from pathlib import Path
from typing import Optional, Tuple, Dict, Union
from enum import Enum
from datetime import datetime
from utils.date_utils import format_date_for_file, get_most_recent_friday, format_date_for_display
import logging
import pandas as pd

from core.ml.funder_classifier import FunderClassifier
from core.data_processing.parsers.base_parser import BaseParser
from core.data_processing.parsers.kings_boom_parser import KingsBoomParser
from core.data_processing.parsers.efin_parser import EfinParser
from core.data_processing.parsers.bhb_parser import BHBParser
from core.data_processing.parsers.acs_vesper_parser import AcsVesperParser
from core.data_processing.parsers.clear_view_parser import ClearViewParser
from .portfolio import Portfolio, PortfolioStructure

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .file_manager import PortfolioFileManager

class ProcessingStatus(Enum):
    PENDING = "pending"
    CLASSIFIED = "classified"
    PARSED = "parsed"
    COMPLETED = "completed"
    FAILED = "failed"

class PortfolioCoordinator:
    """Coordinates file processing between classifier, parser, and file manager"""
    
    def __init__(self, file_manager: 'PortfolioFileManager'):
        self.file_manager = file_manager
        self.classifier = FunderClassifier()
        self.logger = logging.getLogger(__name__)

        # Initialize context attributes
        self._current_portfolio = None
        self._current_processing_date = None

        # Add dictionary to track accumulated files for ClearView
        self._accumulated_files = {}
        
        # Initialize parser mapping
        self.parser_mapping = {
            "ACS": AcsVesperParser,
            "BHB": BHBParser,
            "Boom": KingsBoomParser,
            "ClearView": ClearViewParser,
            "EFIN": EfinParser,
            "Kings": KingsBoomParser,
            "Vesper": AcsVesperParser,
        }


    @property
    def current_portfolio(self) -> Optional[Portfolio]:
        return self._current_portfolio

    @property
    def current_processing_date(self) -> Optional[datetime]:
        return self._current_processing_date

    def _get_parser_for_funder(self, funder: str, file_path: Path) -> Optional[BaseParser]:
        """
        Get the appropriate parser instance for a funder.
        
        Args:
            funder: Name of the funder to get parser for
            file_path: Path to the file to be parsed
            
        Returns:
            Optional[BaseParser]: Parser instance if available, None if no parser found
        """
        try:
            # Validate context
            if not self._validate_context():
                raise ValueError("Processing context not set - portfolio is required")

            # Check for valid parser class
            parser_class = self.parser_mapping.get(funder)
            if not parser_class:
                self.logger.error(f"No parser mapping found for funder: {funder}")
                return None

            # For ClearView, check for existing files to combine
            if funder == "ClearView" and self.current_processing_date:
                self.logger.info(f"Processing ClearView file for {self.current_portfolio.value} "
                               f"on {self.current_processing_date.strftime('%Y-%m-%d')}")
                
                # Get all files from the same processing date
                existing_files = self.file_manager.get_unprocessed_files(
                    portfolio=self.current_portfolio,
                    funder="ClearView",
                    processing_date=self.current_processing_date
                )
                
                # Convert file_path to Path object if it isn't already
                current_file = Path(file_path)
                
                # Add the new file if it's not already in the list
                file_paths = set(str(f) for f in existing_files)
                if str(current_file) not in file_paths:
                    existing_files.append(current_file)
                
                if not existing_files:
                    self.logger.warning("No files found to process")
                    return parser_class(current_file)
                
                self.logger.info(f"Processing {len(existing_files)} ClearView files together")
                for f in existing_files:
                    self.logger.info(f"Including file: {f}")
                
                # Return parser with all files
                return parser_class(existing_files)
            
            # Return instantiated parser for other funders
            self.logger.info(f"Creating parser for {funder}")
            return parser_class(file_path)
            
        except Exception as e:
            self.logger.error(f"Error creating parser for {funder}: {str(e)}")
            raise

    def _accumulate_file(self, file_path: Path, portfolio: Portfolio, funder: str, processing_date: datetime) -> bool:
        """
        Accumulate files for batch processing.
        Returns True if file should be processed now, False if it should be accumulated.
        """
        key = (portfolio.value, funder, processing_date.strftime('%Y-%m-%d'))
        
        if key not in self._accumulated_files:
            self._accumulated_files[key] = []
            
        self._accumulated_files[key].append(file_path)
        
        # Get all expected files for this date range
        start_date = processing_date - timedelta(days=processing_date.weekday())
        end_date = start_date + timedelta(days=4)  # Monday to Friday
        
        # For ClearView, we expect 5 daily files
        if funder == "ClearView":
            expected_count = 5
            current_count = len(self._accumulated_files[key])
            
            self.logger.info(f"Accumulated {current_count} of {expected_count} expected files for {funder}")
            
            # Only process when we have all expected files
            return current_count >= expected_count
            
        # For other funders, process immediately
        return True

    def process_uploaded_file(
        self, 
        file_path: Path, 
        portfolio: Portfolio,
        processing_date: datetime = None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Process an uploaded file for a specific portfolio.
        
        Args:
            file_path: Path to the uploaded file
            portfolio: Portfolio the file is being processed for
            
        Returns:
            Tuple containing:
            - bool: Success status
            - Optional[Dict]: Results dictionary if successful
            - Optional[str]: Error message if unsuccessful
        """
        self.logger.info(f"Starting file processing - Portfolio: {portfolio.value}, "
                        f"Date: {processing_date.strftime('%Y-%m-%d') if processing_date else 'None'}")
                        
        try:
            # First identify the funder
            funder = self.classifier.get_best_match(file_path)
            if not funder:
                return False, None, "Unable to identify funder from file format"

            if not PortfolioStructure.validate_portfolio_funder(portfolio, funder):
                return False, None, f"Funder {funder} is not associated with portfolio {portfolio.value}"

            # Check if we should process or accumulate
            should_process = self._accumulate_file(file_path, portfolio, funder, processing_date)
            
            if not should_process:
                return True, {
                    "funder": funder,
                    "status": "accumulated",
                    "message": "File added to batch for processing"
                }, None

            # Get all accumulated files for processing
            key = (portfolio.value, funder, processing_date.strftime('%Y-%m-%d'))
            all_files = self._accumulated_files.get(key, [file_path])

            # Set processing context
            self.clear_processing_context()
            self.set_processing_context(portfolio, processing_date)

            # Create parser with all accumulated files
            parser_class = self.parser_mapping.get(funder)
            if not parser_class:
                return False, None, f"No parser available for funder {funder}"

            parser = parser_class(all_files)
            pivot_table, total_gross, total_net, total_fee, error = parser.process()
            
            if error:
                return False, None, error

            # Save the combined result
            self.file_manager.save_processed_data(
                portfolio=self.current_portfolio,
                funder=funder,
                file_path=all_files[0],  # Use first file as reference
                pivot_table=pivot_table,
                totals={
                    "gross": total_gross,
                    "net": total_net,
                    "fee": total_fee
                },
                processing_date=self.current_processing_date,
                additional_files=all_files[1:]  # Pass additional files for tracking
            )

            # Clear accumulated files after successful processing
            self._accumulated_files.pop(key, None)

            return True, {
                "funder": funder,
                "totals": {
                    "gross": total_gross,
                    "net": total_net,
                    "fee": total_fee
                },
                "processing_date": self.current_processing_date.strftime("%B %d, %Y") if self.current_processing_date else None,
                "files_processed": len(all_files)
            }, None

        except Exception as e:
            self.logger.error(f"Error processing file: {str(e)}")
            return False, None, str(e)
            
        finally:
            self.clear_processing_context()

    def get_processing_status(self, file_id: int) -> ProcessingStatus:
        """Get current processing status of a file"""
        # Implement status tracking logic
        pass

    def set_processing_context(self, portfolio: Portfolio, processing_date: Optional[datetime] = None):
        """Set the current processing context."""
        self._current_portfolio = portfolio
        self._current_processing_date = processing_date
        self.logger.info(f"Set processing context - Portfolio: {portfolio.value}, "
                        f"Date: {processing_date.strftime('%Y-%m-%d') if processing_date else 'None'}")

    def clear_processing_context(self):
        """Clear the current processing context."""
        self._current_portfolio = None
        self._current_processing_date = None
        self.logger.info("Cleared processing context")

    def _validate_context(self) -> bool:
        """Validate that the processing context is properly set."""
        if self._current_portfolio is None:
            self.logger.error("Processing context not set - portfolio is required")
            return False
        return True

    def get_file_history(self, 
                        portfolio: Optional[Portfolio] = None,
                        funder: Optional[str] = None,
                        date_range: Optional[Tuple[datetime, datetime]] = None
                        ) -> pd.DataFrame:
        """Get processing history with optional filters"""
        # Implement history tracking logic
        pass

    def process_uploaded_file(
        self, 
        file_path: Path, 
        portfolio: Portfolio,
        processing_date: datetime = None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Process an uploaded file for a specific portfolio.
        
        Args:
            file_path: Path to the uploaded file
            portfolio: Portfolio the file is being processed for
            processing_date: The Friday date this file should be processed for
            
        Returns:
            Tuple containing:
            - bool: Success status
            - Optional[Dict]: Results dictionary if successful
            - Optional[str]: Error message if unsuccessful
        """
        self.logger.info(f"Starting file processing - Portfolio: {portfolio.value}, "
                f"Date: {processing_date.strftime('%Y-%m-%d') if processing_date else 'None'}")
                
        try:
            # Clear any existing context and set new context
            self.clear_processing_context()
            self.set_processing_context(portfolio, processing_date)
            
            # Validate context
            if not self._validate_context():
                return False, None, "Processing context not properly set"

            # First identify the funder
            funder = self.classifier.get_best_match(file_path)
            self.logger.info(f"Classifier identified funder as: {funder}")
            
            if not funder:
                return False, None, "Unable to identify funder from file format"
                
            if not PortfolioStructure.validate_portfolio_funder(portfolio, funder):
                return False, None, f"Funder {funder} is not associated with portfolio {portfolio.value}"

            # Get appropriate parser
            parser = self._get_parser_for_funder(funder, file_path)
            if not parser:
                return False, None, f"No parser available for funder {funder}"

            # Process the file
            pivot_table, total_gross, total_net, total_fee, error = parser.process()
            
            if error:
                return False, None, error

            # For ClearView, mark all related files as processed
            if funder == "ClearView" and self.current_processing_date:
                self.file_manager.mark_files_as_processed(
                    portfolio=self.current_portfolio,
                    funder=funder,
                    processing_date=self.current_processing_date
                )

            # Save processed data
            self.file_manager.save_processed_data(
                portfolio=self.current_portfolio,
                funder=funder,
                file_path=file_path,
                pivot_table=pivot_table,
                totals={
                    "gross": total_gross,
                    "net": total_net,
                    "fee": total_fee
                },
                processing_date=self.current_processing_date
            )

            return True, {
                "funder": funder,
                "totals": {
                    "gross": total_gross,
                    "net": total_net,
                    "fee": total_fee
                },
                "processing_date": self.current_processing_date.strftime("%B %d, %Y") if self.current_processing_date else None
            }, None

        except Exception as e:
            self.logger.error(f"Error processing file: {str(e)}")
            return False, None, str(e)
            
        finally:
            # Always clear the context when done
            self.clear_processing_context()
