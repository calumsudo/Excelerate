# app/managers/coordinator.py

from pathlib import Path
from typing import Optional, Tuple, Dict
from enum import Enum
from datetime import datetime
from utils.date_utils import (
    get_most_recent_friday,
)
import logging
import pandas as pd

from core.ml.funder_classifier import FunderClassifier
from core.data_processing.parsers.base_parser import BaseParser
from core.data_processing.parsers.kings_boom_parser import KingsBoomParser
from core.data_processing.parsers.efin_parser import EfinParser
from core.data_processing.parsers.bhb_parser import BHBParser
from core.data_processing.parsers.acs_vesper_parser import AcsVesperParser
from core.data_processing.parsers.clear_view_parser import ClearViewParser
from core.data_processing.parsers.big_parser import BIGParser
from .portfolio import Portfolio, PortfolioStructure
from core.data_processing.excel.workbook_manager import WorkbookManager

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

    def __init__(self, file_manager: "PortfolioFileManager"):
        self.file_manager = file_manager
        self.classifier = FunderClassifier(self.file_manager.db_path)
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
            "BIG": BIGParser,
        }

    @property
    def current_portfolio(self) -> Optional[Portfolio]:
        return self._current_portfolio

    @property
    def current_processing_date(self) -> Optional[datetime]:
        return self._current_processing_date

    def _get_parser_for_funder(
        self, funder: str, file_path: Path
    ) -> Optional[BaseParser]:
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
                self.logger.info(
                    f"Processing ClearView file for {self.current_portfolio.value} "
                    f"on {self.current_processing_date.strftime('%Y-%m-%d')}"
                )

                # Get all files from the same processing date
                existing_files = self.file_manager.get_unprocessed_files(
                    portfolio=self.current_portfolio,
                    funder="ClearView",
                    processing_date=self.current_processing_date,
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

                self.logger.info(
                    f"Processing {len(existing_files)} ClearView files together"
                )
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

    def _accumulate_file(
        self,
        file_path: Path,
        portfolio: Portfolio,
        funder: str,
        processing_date: datetime,
    ) -> bool:
        """
        Accumulate files for batch processing.
        Returns True if file should be processed now, False if it should be accumulated.
        """
        key = (portfolio.value, funder, processing_date.strftime("%Y-%m-%d"))

        if key not in self._accumulated_files:
            self._accumulated_files[key] = []

        self._accumulated_files[key].append(file_path)

        # Get all expected files for this date range
        # start_date = processing_date - timedelta(days=processing_date.weekday())
        # end_date = start_date + timedelta(days=4)  # Monday to Friday

        # For ClearView, we expect 5 daily files
        if funder == "ClearView":
            expected_count = 5
            current_count = len(self._accumulated_files[key])

            self.logger.info(
                f"Accumulated {current_count} of {expected_count} expected files for {funder}"
            )

            # Only process when we have all expected files
            return current_count >= expected_count

        # For other funders, process immediately
        return True

    def get_processing_status(self, file_id: int) -> ProcessingStatus:
        """Get current processing status of a file"""
        # Implement status tracking logic
        pass

    def set_processing_context(
        self, portfolio: Portfolio, processing_date: Optional[datetime] = None
    ):
        """Set the current processing context."""
        self._current_portfolio = portfolio
        self._current_processing_date = processing_date
        self.logger.info(
            f"Set processing context - Portfolio: {portfolio.value}, "
            f"Date: {processing_date.strftime('%Y-%m-%d') if processing_date else 'None'}"
        )

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

    def get_file_history(
        self,
        portfolio: Optional[Portfolio] = None,
        funder: Optional[str] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None,
    ) -> pd.DataFrame:
        """Get processing history with optional filters"""
        # Implement history tracking logic
        pass

    def process_uploaded_file(
        self,
        file_path: Path,
        portfolio: Portfolio,
        processing_date: datetime = None,
        manual_funder: str = None,
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Process an uploaded file for a specific portfolio.

        Args:
            file_path: Path to the uploaded file
            portfolio: Portfolio the file is being processed for
            processing_date: The Friday date this file should be processed for
            manual_funder: If provided, skip classification and use this funder

        Returns:
            Tuple containing:
            - bool: Success status
            - Optional[Dict]: Results dictionary if successful
            - Optional[str]: Error message if unsuccessful
        """
        self.logger.info(
            f"Starting file processing - Portfolio: {portfolio.value}, "
            f"Date: {processing_date.strftime('%Y-%m-%d') if processing_date else 'None'}"
        )

        try:
            if processing_date is None:
                processing_date = get_most_recent_friday()

            self.clear_processing_context()
            self.set_processing_context(portfolio, processing_date)

            # Validate context
            if not self._validate_context():
                return False, None, "Processing context not properly set"

            # Determine funder using manual override or classifier
            if manual_funder:
                funder = manual_funder
                classification_result = None
            else:
                # Use simplified classifier
                classification_result = self.classifier.classify_funder(file_path)

                # If classification failed, show debug information
                if not classification_result.funder:
                    self.classifier.debug_classification(file_path)
                    return (
                        False,
                        None,
                        f"Unable to identify funder. Reason: {classification_result.reason}",
                    )

                funder = classification_result.funder

            # Validate funder belongs to portfolio
            if not PortfolioStructure.validate_portfolio_funder(portfolio, funder):
                return (
                    False,
                    None,
                    f"Funder {funder} is not associated with portfolio {portfolio.value}",
                )

            # Special handling for ClearView
            if funder == "ClearView":
                # Save the current file
                new_path, file_id = self.file_manager.save_uploaded_file(
                    file_path=file_path,
                    portfolio=portfolio,
                    funder=funder,
                    date_received=processing_date,
                    processing_status="pending",
                )

                # Get all files for this week, including the newly uploaded one
                weekly_files = self.file_manager.get_unprocessed_files(
                    portfolio=portfolio, funder=funder, processing_date=processing_date
                )

                file_count = len(weekly_files)
                self.logger.info(f"Processing ClearView files - Day {file_count}")

                # Process all available files together
                parser = ClearViewParser(weekly_files)

            else:
                # For other funders, process normally
                parser = self._get_parser_for_funder(funder, file_path)
                weekly_files = [file_path]
                file_count = 1

            if not parser:
                return False, None, f"No parser available for funder {funder}"

            # Process file(s)
            pivot_table, total_gross, total_net, total_fee, error = parser.process()

            if error:
                return False, None, error

            # Get and validate workbook path
            workbook_path = self.file_manager.get_portfolio_workbook_path(portfolio)
            if not workbook_path:
                return False, None, "Portfolio workbook not found"

            # Update workbook
            workbook_manager = WorkbookManager(self.file_manager)

            # Only backup on first file of the week
            if funder != "ClearView" or file_count == 1:
                workbook_manager.backup_workbook(workbook_path, processing_date)

            unmatched, error = workbook_manager.update_workbook(
                workbook_path, pivot_table, funder, processing_date
            )

            if error:
                return False, None, error

            # Save the processed results after each file
            self.file_manager.save_processed_data(
                portfolio=self.current_portfolio,
                funder=funder,
                file_path=weekly_files[0],  # Use first file as primary
                pivot_table=pivot_table,
                totals={"gross": total_gross, "net": total_net, "fee": total_fee},
                processing_date=processing_date,
                additional_files=weekly_files[1:],
            )

            # Create result dictionary
            result = {
                "funder": funder,
                "totals": {"gross": total_gross, "net": total_net, "fee": total_fee},
                "unmatched_ids": unmatched,
                "processing_date": processing_date.strftime("%B %d, %Y"),
                "files_processed": file_count if funder == "ClearView" else 1,
            }

            # Add classification details if available
            if classification_result:
                result.update(
                    {
                        "classification_confidence": classification_result.confidence,
                        "new_merchant_ids": len(classification_result.new_ids),
                        "matched_merchant_ids": len(classification_result.matched_ids),
                    }
                )

            return True, result, None

        except Exception as e:
            self.logger.error(f"Error processing file: {str(e)}")
            return False, None, str(e)
        finally:
            self.clear_processing_context()
