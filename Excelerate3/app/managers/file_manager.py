# managers/file_manager.py
import json
import csv
import sqlite3
import logging
from datetime import datetime
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, asdict
from .portfolio import Portfolio, PortfolioStructure

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
        self._setup_database()
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Load user preferences
        self.preferences = self._load_preferences()

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

    def _setup_database(self):
        """Initialize SQLite database for file tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS uploaded_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_filename TEXT,
                    stored_filename TEXT,
                    portfolio TEXT,
                    funder TEXT,
                    upload_date TEXT,
                    processing_date TEXT,
                    processing_status TEXT,
                    error_message TEXT,
                    file_path TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pivot_tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file_id INTEGER,
                    stored_filename TEXT,
                    creation_date TEXT,
                    processing_date TEXT,
                    portfolio TEXT,
                    funder TEXT,
                    file_path TEXT,
                    FOREIGN KEY (source_file_id) REFERENCES uploaded_files (id)
                )
            ''')

    def _setup_logging(self) -> logging.Logger:
        """Configure logging with rotation and formatting"""
        log_file = self.logs_dir / f"portfolio_manager_{datetime.now().strftime('%Y%m%d')}.log"
        
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
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
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                return UserPreferences(**data)
        except Exception as e:
            self.logger.error(f"Error loading preferences: {e}")
        return UserPreferences()

    def save_preferences(self):
        """Save current preferences to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.preferences), f, indent=4)
            self.logger.info("Preferences saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving preferences: {e}")

    def save_uploaded_file(self, file_path: Path, portfolio: Portfolio,
                          funder: str, date_received: datetime = None) -> Tuple[Path, int]:
        """
        Save an uploaded file to the appropriate portfolio/funder directory
        Returns: (new_file_path, database_id)
        """
        if date_received is None:
            date_received = datetime.now()
            
        if not PortfolioStructure.validate_portfolio_funder(portfolio, funder):
            raise ValueError(f"Funder {funder} is not associated with portfolio {portfolio.value}")
        
        # Generate new filename
        timestamp = date_received.strftime("%Y%m%d_%H%M%S")
        new_filename = f"{portfolio.value}_{funder}_{timestamp}_{file_path.name}"
        
        # Determine save path
        save_dir = self.base_dir / portfolio.value / "uploads" / funder
        new_path = save_dir / new_filename
        
        try:
            # Copy file
            import shutil
            shutil.copy2(file_path, new_path)
            
            # Record in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT INTO uploaded_files (
                        original_filename, stored_filename, portfolio, funder,
                        upload_date, processing_status, file_path, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (file_path.name, new_filename, portfolio.value, funder,
                     date_received.isoformat(), 'pending', str(new_path),
                     datetime.now().isoformat()))
                file_id = cursor.lastrowid
            
            # Update recent files
            self._update_recent_files(str(new_path))
            
            self.logger.info(f"Saved file {file_path.name} as {new_filename} "
                           f"for {portfolio.value}/{funder}")
            
            return new_path, file_id
            
        except Exception as e:
            error_msg = f"Error saving uploaded file: {str(e)}"
            self.logger.error(error_msg)
            raise

    def save_pivot_table(self, data: List[List], portfolio: Portfolio,
                        funder: str, source_file_id: int,
                        date_generated: datetime = None) -> Path:
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
            # Save pivot table
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(data)
            
            # Record in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO pivot_tables (
                        source_file_id, stored_filename, creation_date,
                        portfolio, funder, file_path
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (source_file_id, filename, date_generated.isoformat(),
                     portfolio.value, funder, str(file_path)))
            
            self.logger.info(f"Saved pivot table {filename} for {portfolio.value}/{funder}")
            
            return file_path
            
        except Exception as e:
            error_msg = f"Error saving pivot table: {str(e)}"
            self.logger.error(error_msg)
            raise

    def get_recent_files(self, portfolio: Optional[Portfolio] = None,
                        funder: Optional[str] = None,
                        days: int = 7) -> List[Dict]:
        """Get recent files with optional filters"""
        query = '''
            SELECT original_filename, stored_filename, portfolio, funder,
                   upload_date, processing_status, file_path
            FROM uploaded_files
            WHERE upload_date >= date('now', ?)
        '''
        params = [f'-{days} days']
        
        if portfolio:
            query += ' AND portfolio = ?'
            params.append(portfolio.value)
        if funder:
            query += ' AND funder = ?'
            params.append(funder)
            
        query += ' ORDER BY upload_date DESC'
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def _update_recent_files(self, file_path: str):
        """Update the list of recent files in preferences"""
        if file_path in self.preferences.recent_files:
            self.preferences.recent_files.remove(file_path)
        self.preferences.recent_files.insert(0, file_path)
        self.preferences.recent_files = self.preferences.recent_files[:10]  # Keep last 10
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
        processing_date: Optional[datetime] = None
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
            # First save the uploaded file and get the file ID
            new_path, file_id = self.save_uploaded_file(
                file_path=file_path,
                portfolio=portfolio,
                funder=funder,
                date_received=processing_date
            )
            
            # Convert pivot table to list for saving
            pivot_data = [pivot_table.columns.tolist()]  # Headers
            pivot_data.extend(pivot_table.values.tolist())
            
            # Save pivot table and get the path
            pivot_path = self.save_pivot_table(
                data=pivot_data,
                portfolio=portfolio,
                funder=funder,
                source_file_id=file_id,
                date_generated=processing_date
            )
            
            # Update processing status in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE uploaded_files
                    SET processing_status = ?,
                        updated_at = ?,
                        processing_date = ?
                    WHERE id = ?
                ''', ('completed', datetime.now().isoformat(), processing_date.isoformat(), file_id))
                
                # Make sure processing_totals table has processing_date column
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS processing_totals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_id INTEGER,
                        gross_total REAL,
                        net_total REAL,
                        fee_total REAL,
                        processing_date TEXT,
                        created_at TEXT,
                        FOREIGN KEY (file_id) REFERENCES uploaded_files (id)
                    )
                ''')
                
                # Insert totals
                conn.execute('''
                    INSERT INTO processing_totals (
                        file_id, gross_total, net_total, fee_total,
                        processing_date, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    file_id,
                    totals['gross'],
                    totals['net'],
                    totals['fee'],
                    processing_date.isoformat(),
                    datetime.now().isoformat()
                ))
            
            self.logger.info(
                f"Successfully saved processed data for {portfolio.value}/{funder}. "
                f"File ID: {file_id}, Pivot table saved to: {pivot_path}, "
                f"Processing Date: {processing_date.strftime('%Y-%m-%d')}"
            )
            
        except Exception as e:
            error_msg = f"Error saving processed data: {str(e)}"
            self.logger.error(error_msg)
            
            # Update status to failed in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE uploaded_files
                    SET processing_status = ?,
                        error_message = ?,
                        updated_at = ?
                    WHERE original_filename = ?
                ''', ('failed', str(e), datetime.now().isoformat(), file_path.name))
                
            raise Exception(error_msg)

    def get_processing_results(
        self,
        portfolio: Optional[Portfolio] = None,
        funder: Optional[str] = None,
        days: int = 7
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
        query = '''
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
        '''
        params = [f'-{days} days']
        
        if portfolio:
            query += ' AND uf.portfolio = ?'
            params.append(portfolio.value)
        if funder:
            query += ' AND uf.funder = ?'
            params.append(funder)
            
        query += ' ORDER BY uf.upload_date DESC'
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(query, params).fetchall()]