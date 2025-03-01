# app/managers/file_manager.py

import json
import sqlite3
import logging
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, asdict
from .portfolio import Portfolio, PortfolioStructure
from .database_manager import DatabaseManager


@dataclass
class UserPreferences:
    theme_mode: str = "System"
    auth_token: Optional[str] = None
    last_upload_directory: Optional[str] = None
    recent_files: List[str] = None

    def __post_init__(self):
        if self.recent_files is None:
            self.recent_files = []


class PortfolioFileManager:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.db_path = base_dir / "file_tracking.db"
        self.config_file = base_dir / "config" / "preferences.json"

        # Setup directory structure
        self._setup_directories()

        # Setup database
        self.db_manager = DatabaseManager(self.db_path)
        # self._setup_database()

        # Setup logging
        self.logger = self._setup_logging()

        # Load user preferences
        self.preferences = self._load_preferences()

        self.logger.info("FileManager initialized successfully")

    def _setup_directories(self):
        """Create necessary directory structure"""
        # Base directories
        self.logs_dir = self.base_dir / "logs"
        self.config_dir = self.base_dir / "config"

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Portfolio-specific directories
        for portfolio in Portfolio:
            # Create main portfolio directories
            portfolio_base = self.base_dir / portfolio.value

            # Create uploads directory with funder subdirectories
            uploads_dir = portfolio_base / "uploads"
            uploads_dir.mkdir(parents=True, exist_ok=True)

            # Create outputs directory with funder subdirectories
            outputs_dir = portfolio_base / "outputs"
            outputs_dir.mkdir(parents=True, exist_ok=True)

            # Create funder subdirectories
            for funder in PortfolioStructure.get_portfolio_funders(portfolio):
                (uploads_dir / funder).mkdir(exist_ok=True)
                (outputs_dir / funder).mkdir(exist_ok=True)

    def _setup_logging(self) -> logging.Logger:
        """Configure logging with rotation and formatting"""
        log_file = (
            self.logs_dir / f"portfolio_manager_{datetime.now().strftime('%Y%m%d')}.log"
        )

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def _load_preferences(self) -> UserPreferences:
        """Load user preferences from JSON file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                return UserPreferences(**data)
        except Exception as e:
            self.logger.error(f"Error loading preferences: {e}")
        return UserPreferences()

    def save_preferences(self):
        """Save current preferences to JSON file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(asdict(self.preferences), f, indent=4)
            self.logger.info("Preferences saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving preferences: {e}")

    def save_uploaded_file(
        self,
        file_path: Path,
        portfolio: Portfolio,
        funder: str,
        date_received: Optional[datetime] = None,
        is_additional: bool = False,
        primary_file_id: Optional[int] = None,
        processing_status: str = "pending",
    ) -> Tuple[Path, int]:
        """
        Save an uploaded file and record it in the database.

        Args:
            file_path: Path to the file to save
            portfolio: Portfolio the file belongs to
            funder: Name of the funder
            date_received: When the file was received (defaults to now)
            is_additional: Whether this is an additional file in a batch
            primary_file_id: ID of the primary file if this is an additional file
            processing_status: Initial processing status for the file

        Returns:
            Tuple[Path, int]: (Path to saved file, database ID)
        """
        if date_received is None:
            date_received = datetime.now()

        timestamp = date_received.strftime("%Y%m%d_%H%M%S")
        new_filename = f"{portfolio.value}_{funder}_{timestamp}_{file_path.name}"
        save_dir = self.base_dir / portfolio.value / "uploads" / funder
        new_path = save_dir / new_filename

        try:
            import shutil

            shutil.copy2(file_path, new_path)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO uploaded_files (
                        original_filename,
                        stored_filename,
                        portfolio,
                        funder,
                        upload_date,
                        processing_date,
                        processing_status,
                        file_path,
                        updated_at,
                        is_additional,
                        primary_file_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        file_path.name,
                        new_filename,
                        portfolio.value,
                        funder,
                        datetime.now().isoformat(),
                        date_received.isoformat(),
                        processing_status,
                        str(new_path),
                        datetime.now().isoformat(),
                        is_additional,
                        primary_file_id,
                    ),
                )
                file_id = cursor.lastrowid

            self._update_recent_files(str(new_path))
            self.logger.info(
                f"Saved file {file_path.name} as {new_filename} "
                f"for {portfolio.value}/{funder}"
                f"{' (additional file)' if is_additional else ''}"
            )

            return new_path, file_id

        except Exception as e:
            error_msg = f"Error saving uploaded file: {str(e)}"
            self.logger.error(error_msg)
            raise

    def save_pivot_table(
        self,
        data: pd.DataFrame,
        portfolio: Portfolio,
        funder: str,
        source_file_id: int,
        date_generated: datetime = None,
    ) -> Path:
        """Save a generated pivot table"""
        if date_generated is None:
            date_generated = datetime.now()

        # Generate filename
        timestamp = date_generated.strftime("%Y%m%d_%H%M%S")
        filename = f"{portfolio.value}_{funder}_pivot_{timestamp}.csv"

        # Determine save path
        save_dir = self.base_dir / portfolio.value / "outputs" / funder
        file_path = save_dir / filename

        try:
            # If data is already a DataFrame, save it directly
            if isinstance(data, pd.DataFrame):
                data.to_csv(file_path, index=False)
            else:
                # Convert list data to DataFrame and save
                df = pd.DataFrame(data[1:], columns=data[0])
                df.to_csv(file_path, index=False)

            # Record in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO pivot_tables (
                        source_file_id, stored_filename, creation_date,
                        portfolio, funder, file_path
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        source_file_id,
                        filename,
                        date_generated.isoformat(),
                        portfolio.value,
                        funder,
                        str(file_path),
                    ),
                )

            self.logger.info(
                f"Saved pivot table {filename} for {portfolio.value}/{funder}"
            )

            return file_path

        except Exception as e:
            error_msg = f"Error saving pivot table: {str(e)}"
            self.logger.error(error_msg)
            raise

    def get_recent_files(
        self,
        portfolio: Optional[Portfolio] = None,
        funder: Optional[str] = None,
        days: int = 7,
    ) -> List[Dict]:
        """Get recent files with optional filters"""
        query = """
            SELECT original_filename, stored_filename, portfolio, funder,
                   upload_date, processing_status, file_path
            FROM uploaded_files
            WHERE upload_date >= date('now', ?)
        """
        params = [f"-{days} days"]

        if portfolio:
            query += " AND portfolio = ?"
            params.append(portfolio.value)
        if funder:
            query += " AND funder = ?"
            params.append(funder)

        query += " ORDER BY upload_date DESC"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def get_unprocessed_files(
        self, portfolio: Portfolio, funder: str, processing_date: datetime
    ) -> List[Path]:
        """
        Get unprocessed files for a specific portfolio, funder, and date.

        Args:
            portfolio: Portfolio to check
            funder: Name of the funder
            processing_date: The processing date to check for

        Returns:
            List[Path]: List of paths to unprocessed files
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT file_path, original_filename
                    FROM uploaded_files
                    WHERE portfolio = ?
                    AND funder = ?
                    AND DATE(processing_date) = DATE(?)
                    AND (processing_status = 'pending' OR processing_status IS NULL)
                """,
                    (portfolio.value, funder, processing_date.strftime("%Y-%m-%d")),
                )

                files = []
                for row in cursor.fetchall():
                    file_path = Path(row[0])
                    if file_path.exists():
                        files.append(file_path)
                    else:
                        self.logger.warning(
                            f"File not found at path: {file_path}, original filename: {row[1]}"
                        )

                self.logger.info(
                    f"Found {len(files)} unprocessed files for {portfolio.value}/{funder} "
                    f"on {processing_date.strftime('%Y-%m-%d')}"
                )
                return files

        except Exception as e:
            self.logger.error(f"Error getting unprocessed files: {str(e)}")
            return []

    def mark_files_as_processed(
        self, portfolio: Portfolio, funder: str, processing_date: datetime
    ) -> None:
        """
        Mark all related files as processed.

        Args:
            portfolio: Portfolio being processed
            funder: Name of the funder
            processing_date: The processing date
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    UPDATE uploaded_files
                    SET processing_status = 'completed',
                        updated_at = ?
                    WHERE portfolio = ?
                    AND funder = ?
                    AND DATE(processing_date) = DATE(?)
                    AND (processing_status = 'pending' OR processing_status IS NULL)
                """,
                    (
                        datetime.now().isoformat(),
                        portfolio.value,
                        funder,
                        processing_date.strftime("%Y-%m-%d"),
                    ),
                )

                rows_updated = cursor.rowcount
                self.logger.info(
                    f"Marked {rows_updated} files as processed for {portfolio.value}/{funder} "
                    f"on {processing_date.strftime('%Y-%m-%d')}"
                )

        except Exception as e:
            self.logger.error(f"Error marking files as processed: {str(e)}")
            raise

    def _update_recent_files(self, file_path: str):
        """Update the list of recent files in preferences"""
        if file_path in self.preferences.recent_files:
            self.preferences.recent_files.remove(file_path)
        self.preferences.recent_files.insert(0, file_path)
        self.preferences.recent_files = self.preferences.recent_files[
            :10
        ]  # Keep last 10
        self.save_preferences()

    def clear_recent_files(self):
        """Clear the recent files list"""
        self.preferences.recent_files = []
        self.save_preferences()

    def save_processed_data(
        self,
        portfolio: Portfolio,
        funder: str,
        file_path: Path,
        pivot_table: pd.DataFrame,
        totals: Dict[str, float],
        processing_date: Optional[datetime] = None,
        additional_files: Optional[List[Path]] = None,
    ) -> None:
        """
        Save processed data including pivot table and totals.

        Args:
            portfolio: Portfolio the data belongs to
            funder: Name of the funder
            file_path: Original file path
            pivot_table: Processed pivot table DataFrame
            totals: Dictionary containing gross, net, and fee totals
            processing_date: The Friday date this data should be processed for
        """
        try:
            if processing_date is None:
                processing_date = datetime.now()

            additional_files = (
                additional_files or []
            )  # Initialize to empty list if None

            # Save the primary file and get its ID
            new_path, file_id = self.save_uploaded_file(
                file_path=file_path,
                portfolio=portfolio,
                funder=funder,
                date_received=processing_date,
            )

            # Save additional files if any
            additional_ids = []
            for add_file in additional_files:
                _, add_id = self.save_uploaded_file(
                    file_path=add_file,
                    portfolio=portfolio,
                    funder=funder,
                    date_received=processing_date,
                    is_additional=True,
                    primary_file_id=file_id,
                )
                additional_ids.append(add_id)

            # Generate weekly identifier for pivot table
            week_start = processing_date - timedelta(days=processing_date.weekday())
            week_identifier = week_start.strftime("%Y%m%d")

            # Save pivot table with week identifier
            pivot_filename = f"{portfolio.value}_{funder}_pivot_{week_identifier}.csv"
            save_dir = self.base_dir / portfolio.value / "outputs" / funder
            pivot_path = save_dir / pivot_filename

            # Save the pivot table
            pivot_table.to_csv(pivot_path, index=False)

            # Update database records
            with sqlite3.connect(self.db_path) as conn:
                # Update primary file status
                conn.execute(
                    """
                    UPDATE uploaded_files
                    SET processing_status = ?,
                        updated_at = ?,
                        processing_date = ?
                    WHERE id = ?
                """,
                    (
                        "completed",
                        datetime.now().isoformat(),
                        processing_date.isoformat(),
                        file_id,
                    ),
                )

                # Update additional files status
                if additional_ids:
                    placeholders = ",".join("?" * len(additional_ids))
                    conn.execute(
                        f"""
                        UPDATE uploaded_files
                        SET processing_status = ?,
                            updated_at = ?,
                            processing_date = ?
                        WHERE id IN ({placeholders})
                    """,
                        [
                            "completed",
                            datetime.now().isoformat(),
                            processing_date.isoformat(),
                            *additional_ids,
                        ],
                    )

                # Record pivot table
                conn.execute(
                    """
                    INSERT INTO pivot_tables (
                        source_file_id,
                        stored_filename,
                        creation_date,
                        processing_date,
                        portfolio,
                        funder,
                        file_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        file_id,
                        pivot_filename,
                        datetime.now().isoformat(),
                        processing_date.isoformat(),
                        portfolio.value,
                        funder,
                        str(pivot_path),
                    ),
                )

                # Store totals
                conn.execute(
                    """
                    INSERT INTO processing_totals (
                        file_id,
                        gross_total,
                        net_total,
                        fee_total,
                        processing_date,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        file_id,
                        totals["gross"],
                        totals["net"],
                        totals["fee"],
                        processing_date.isoformat(),
                        datetime.now().isoformat(),
                    ),
                )

                self.logger.info(
                    f"Successfully saved processed data for {portfolio.value}/{funder}. "
                    f"Primary File ID: {file_id}, "
                    f"Additional Files: {len(additional_ids) if additional_ids else 0}, "
                    f"Pivot table saved to: {pivot_path}, "
                    f"Processing Date: {processing_date.strftime('%Y-%m-%d')}"
                )

        except Exception as e:
            error_msg = f"Error saving processed data: {str(e)}"
            self.logger.error(error_msg)

            # Update status to failed in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE uploaded_files
                    SET processing_status = ?,
                        error_message = ?,
                        updated_at = ?
                    WHERE original_filename = ?
                """,
                    ("failed", str(e), datetime.now().isoformat(), file_path.name),
                )

            raise Exception(error_msg)

    def get_processing_results(
        self,
        portfolio: Optional[Portfolio] = None,
        funder: Optional[str] = None,
        days: int = 7,
    ) -> List[Dict]:
        """
        Get processing results including totals with optional filters.

        Args:
            portfolio: Optional portfolio filter
            funder: Optional funder filter
            days: Number of days to look back

        Returns:
            List of dictionaries containing processing results
        """
        query = """
            SELECT 
                uf.original_filename,
                uf.portfolio,
                uf.funder,
                uf.upload_date,
                uf.processing_status,
                pt.gross_total,
                pt.net_total,
                pt.fee_total,
                piv.file_path as pivot_path
            FROM uploaded_files uf
            LEFT JOIN processing_totals pt ON uf.id = pt.file_id
            LEFT JOIN pivot_tables piv ON uf.id = piv.source_file_id
            WHERE uf.upload_date >= date('now', ?)
        """
        params = [f"-{days} days"]

        if portfolio:
            query += " AND uf.portfolio = ?"
            params.append(portfolio.value)
        if funder:
            query += " AND uf.funder = ?"
            params.append(funder)

        query += " ORDER BY uf.upload_date DESC"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def save_portfolio_workbook(self, portfolio: Portfolio, workbook_path: Path) -> None:
        """Save a portfolio's Excel workbook and populate merchant database."""
        try:
            # Create portfolio config directory if it doesn't exist
            config_dir = self.base_dir / portfolio.value / "config"
            config_dir.mkdir(parents=True, exist_ok=True)

            # Copy workbook to config directory with standardized name
            import shutil

            # Use cleaner naming convention - wr_portfolio.xlsx for White Rabbit
            if portfolio == Portfolio.WHITE_RABBIT:
                filename = "wr_portfolio.xlsx"
            else:
                filename = f"{portfolio.value.lower()}_portfolio.xlsx"
                
            new_path = config_dir / filename
            shutil.copy2(workbook_path, new_path)

            # Initialize WorkbookManager
            from core.data_processing.excel.workbook_manager import WorkbookManager

            workbook_manager = WorkbookManager(self)

            # Populate merchant database
            stats = workbook_manager.populate_merchant_database(new_path, portfolio)

            # Log results
            total_merchants = sum(stats.values())
            self.logger.info(
                f"Saved {portfolio.value} portfolio workbook to {new_path}"
            )
            self.logger.info(f"Added {total_merchants} merchants to tracking database")
            for funder, count in stats.items():
                self.logger.info(f"- {funder}: {count} merchants")

        except Exception as e:
            self.logger.error(f"Error saving portfolio workbook: {str(e)}")
            raise

    def get_portfolio_workbook_path(self, portfolio: Portfolio) -> Optional[Path]:
        """Get the path to a portfolio's Excel workbook if it exists."""
        if portfolio == Portfolio.WHITE_RABBIT:
            filename = "wr_portfolio.xlsx"
        else:
            filename = f"{portfolio.value.lower()}_portfolio.xlsx"
            
        workbook_path = self.base_dir / portfolio.value / "config" / filename
        return workbook_path if workbook_path.exists() else None
    

    def export_portfolio_workbook(self, portfolio: Portfolio, dest_path: Optional[Path] = None) -> Optional[Path]:
        """
        Export a portfolio's Excel workbook to the specified destination or Desktop.
        
        Args:
            portfolio: Portfolio enum value
            dest_path: Optional destination path, defaults to Desktop
            
        Returns:
            Path to the exported file if successful, None otherwise
        """
        try:
            # Get the source workbook path
            source_path = self.get_portfolio_workbook_path(portfolio)
            if not source_path or not source_path.exists():
                self.logger.error(f"Portfolio workbook for {portfolio.value} not found")
                return None
                
            # Determine destination path
            if dest_path is None:
                # Default to Desktop
                import os
                desktop_path = Path(os.path.expanduser("~/Desktop"))
                
                # Use standardized naming for export
                if portfolio == Portfolio.WHITE_RABBIT:
                    export_filename = "wr_portfolio.xlsx"
                else:
                    export_filename = f"{portfolio.value.lower()}_portfolio.xlsx"
                    
                dest_path = desktop_path / export_filename
                
            # Copy the file
            import shutil
            shutil.copy2(source_path, dest_path)
            
            self.logger.info(f"Exported {portfolio.value} portfolio workbook to {dest_path}")
            return dest_path
            
        except Exception as e:
            self.logger.error(f"Error exporting portfolio workbook: {str(e)}")
            return None