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
            parser_class = self.parser_mapping.get(funder)
            if not parser_class:
                self.logger.error(f"No parser mapping found for funder: {funder}")
                return None
                
            # Return instantiated parser
            return parser_class(file_path)
            
        except Exception as e:
            self.logger.error(f"Error creating parser for {funder}: {str(e)}")
            return None

    def process_uploaded_file(
        self, 
        file_path: Path, 
        portfolio: Portfolio
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
        try:
            # First identify the funder
            funder = self.classifier.get_best_match(file_path)
            
            if not funder:
                return False, None, "Unable to identify funder from file format"
                
            # Check if funder is authorized for this portfolio using PortfolioStructure
            if not PortfolioStructure.validate_portfolio_funder(portfolio, funder):
                return False, None, f"Funder {funder} is not associated with portfolio {portfolio.value}"

            # Get appropriate parser
            parser = self._get_parser_for_funder(funder, file_path)
            if not parser:
                return False, None, f"No parser available for funder {funder}"

            pivot_table, total_gross, total_net, total_fee, error = parser.process()
            
            if error:
                return False, None, error

            self.file_manager.save_processed_data(
                portfolio=portfolio,
                funder=funder,
                file_path=file_path,
                pivot_table=pivot_table,
                totals={
                    "gross": total_gross,
                    "net": total_net,
                    "fee": total_fee
                }
            )

            return True, {
                "funder": funder,
                "totals": {
                    "gross": total_gross,
                    "net": total_net,
                    "fee": total_fee
                }
            }, None

        except Exception as e:
            self.logger.error(f"Error processing file: {str(e)}")
            return False, None, str(e)
        
    def get_processing_status(self, file_id: int) -> ProcessingStatus:
        """Get current processing status of a file"""
        # Implement status tracking logic
        pass

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
        try:
            # Use provided date or default to most recent Friday
            if processing_date is None:
                processing_date = get_most_recent_friday()

            # First identify the funder
            funder = self.classifier.get_best_match(file_path)
            
            if not funder:
                return False, None, "Unable to identify funder from file format"
                
            # Check if funder is authorized for this portfolio
            if not PortfolioStructure.validate_portfolio_funder(portfolio, funder):
                return False, None, f"Funder {funder} is not associated with portfolio {portfolio.value}"

            # Get appropriate parser
            parser = self._get_parser_for_funder(funder, file_path)
            if not parser:
                return False, None, f"No parser available for funder {funder}"

            pivot_table, total_gross, total_net, total_fee, error = parser.process()
            
            if error:
                return False, None, error

            # Save with processing date
            self.file_manager.save_processed_data(
                portfolio=portfolio,
                funder=funder,
                file_path=file_path,
                pivot_table=pivot_table,
                totals={
                    "gross": total_gross,
                    "net": total_net,
                    "fee": total_fee
                },
                processing_date=processing_date
            )

            return True, {
                "funder": funder,
                "totals": {
                    "gross": total_gross,
                    "net": total_net,
                    "fee": total_fee
                },
                "processing_date": format_date_for_display(processing_date)
            }, None

        except Exception as e:
            self.logger.error(f"Error processing file: {str(e)}")
            return False, None, str(e)