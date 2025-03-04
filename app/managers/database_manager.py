# app/managers/database_manager.py

import sqlite3
import logging
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize all database tables and indexes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Create merchant tracking table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS merchant_tracking (
                        advance_id TEXT PRIMARY KEY,
                        funder TEXT NOT NULL,
                        merchant_name TEXT,
                        portfolio TEXT NOT NULL,
                        first_seen_date TEXT NOT NULL,
                        last_updated TEXT NOT NULL
                    )
                """)

                # Create uploaded_files table
                conn.execute("""
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
                        updated_at TEXT,
                        is_additional BOOLEAN DEFAULT FALSE,
                        primary_file_id INTEGER,
                        FOREIGN KEY (primary_file_id) REFERENCES uploaded_files (id)
                    )
                """)

                # Create pivot_tables table
                conn.execute("""
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
                """)

                # Create processing_totals table
                conn.execute("""
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
                """)

                # Create indexes
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_merchant_portfolio_funder 
                    ON merchant_tracking(portfolio, funder)
                """)

                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_uploaded_files_portfolio_funder 
                    ON uploaded_files(portfolio, funder)
                """)

                self.logger.info("Database initialization completed successfully")

        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            raise

    def reset_database(self):
        """Drop and recreate all tables - use with caution!"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Drop all tables
                tables = [
                    "merchant_tracking",
                    "processing_totals",
                    "pivot_tables",
                    "uploaded_files",
                ]

                for table in tables:
                    conn.execute(f"DROP TABLE IF EXISTS {table}")

                self.logger.info("Existing tables dropped")

                # Reinitialize database
                self._init_database()
                self.logger.info("Database reset completed successfully")

        except Exception as e:
            self.logger.error(f"Error resetting database: {str(e)}")
            raise

    def verify_database(self) -> bool:
        """Verify database schema and integrity."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check all tables exist
                required_tables = {
                    "merchant_tracking",
                    "uploaded_files",
                    "pivot_tables",
                    "processing_totals",
                }

                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table'
                """)
                existing_tables = {row[0] for row in cursor.fetchall()}

                missing_tables = required_tables - existing_tables
                if missing_tables:
                    self.logger.error(f"Missing tables: {missing_tables}")
                    return False

                self.logger.info("Database verification completed successfully")
                return True

        except Exception as e:
            self.logger.error(f"Error verifying database: {str(e)}")
            return False
