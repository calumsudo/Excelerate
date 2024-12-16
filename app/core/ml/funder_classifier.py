from pathlib import Path
import pandas as pd
import sqlite3
import re
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

@dataclass
class ClassificationResult:
    funder: str
    confidence: float
    new_ids: List[str]  # IDs not found in database
    matched_ids: List[str]  # IDs found in database
    reason: str

class EnhancedFunderClassifier:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize database if needed
        self._init_database()
        
        # Funder-specific patterns
        self.id_patterns = {
            "ACS": r'^AC\d+$',
            "Vesper": r'^VC\d+$',
            "BHB": r'^4\d{4,5}$',
            "Kings": r'^7\d{6}$',
            "Boom": r'^7\d{6}$',
            "EFIN": r'^7\d{6}$',
            "ClearView": r'^7\d{6}$'
        }
        
        # Expected column patterns for each funder
        self.column_patterns = {
            "ACS": ["Advance ID", "Merchant Name", "Gross Payment", "Fees", "Net"],
            "Vesper": ["Advance ID", "Merchant Name", "Gross Payment", "Fees", "Net"],
            "BHB": ["Deal ID", "Deal Name", "Participator Gross Amount", "Fee", "Net Payment Amount"],
            "Kings": ["Advance ID", "Business Name", "Payable Amt (Gross)", "Servicing Fee $", "Payable Amt (Net)"],
            "Boom": ["Advance ID", "Business Name", "Payable Amt (Gross)", "Servicing Fee $", "Payable Amt (Net)"],
            "EFIN": ["Advance ID", "Business Name", "Payable Amt (Gross)", "Servicing Fee $", "Payable Amt (Net)"],
            "ClearView": ["AdvanceID", "Syn Gross Amount", "Syn Net Amount"]
        }

    def _init_database(self):
        """Initialize the merchant tracking database if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS merchant_tracking (
                        advance_id TEXT PRIMARY KEY,
                        funder TEXT NOT NULL,
                        merchant_name TEXT,
                        first_seen_date TEXT NOT NULL,
                        last_updated TEXT NOT NULL
                    )
                ''')
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            raise

    def _find_advance_id_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the column containing advance IDs."""
        possible_names = ["Advance ID", "AdvanceID", "Deal ID"]
        for col in possible_names:
            if col in df.columns:
                return col
        return None
    
    def _find_header_row(self, df: pd.DataFrame, funder: Optional[str] = None) -> int:
        """Find the actual header row in a dataframe."""
        # Special handling for ACS/Vesper weekly format
        if 'Withdrawn per deal' in df.columns:
            # Look for the row containing "Advance ID"
            for idx, row in df.iterrows():
                if any('Advance ID' in str(val) for val in row.values):
                    return idx
        return 0


    def _get_suspected_funder(self, file_path: Path, df: Optional[pd.DataFrame] = None) -> Optional[str]:
        """Try to determine the funder based on file characteristics."""
        if df is None:
            df = pd.read_csv(file_path)
            
        # Check for ACS/Vesper weekly format
        if 'Withdrawn per deal' in df.columns:
            # Look at the first few IDs to determine if ACS or Vesper
            header_row = self._find_header_row(df)
            data_df = pd.read_csv(file_path, skiprows=header_row)
            first_id = str(data_df.iloc[0, 0]).strip()
            if first_id.startswith('AC'):
                return "ACS"
            elif first_id.startswith('VC'):
                return "Vesper"
                
        return None

    def _extract_advance_ids(self, file_path: Path) -> Tuple[List[str], Optional[str]]:
        """
        Extract advance IDs from the CSV file and try to determine funder.
        Returns tuple of (ids, suspected_funder)
        """
        try:
            # First try weekly format
            df, funder = self._try_read_weekly_format(file_path)
            if df is not None:
                ids = df['Advance ID'].astype(str).str.strip()
                ids = ids[ids.notna() & (ids != "") & (ids != "nan") & (ids != "Grand Total")]
                return ids.tolist(), funder
                
            # Try regular format
            df = self._try_read_regular_format(file_path)
            if df is None:
                raise ValueError("Could not read file in any known format")
                
            # Try to find ID column
            id_columns = {
                "BHB": ["Deal ID", "DealID"],
                "Kings": ["Advance ID"],
                "Boom": ["Advance ID"],
                "EFIN": ["Advance ID"],
                "ClearView": ["AdvanceID"]
            }
            
            # Look for ID column
            id_col = None
            suspected_funder = None
            
            for funder, cols in id_columns.items():
                for col in cols:
                    if col in df.columns:
                        id_col = col
                        suspected_funder = funder
                        break
                if id_col:
                    break
                    
            if not id_col:
                # Try case-insensitive match
                for col in df.columns:
                    for funder, cols in id_columns.items():
                        if any(id_col.lower() == col.lower() for id_col in cols):
                            id_col = col
                            suspected_funder = funder
                            break
                    if id_col:
                        break
                        
            if not id_col:
                raise ValueError(f"Could not find advance ID column. Available columns: {df.columns.tolist()}")
                
            # Extract and clean IDs
            ids = df[id_col].astype(str).str.strip()
            ids = ids[ids.notna() & (ids != "") & (ids != "nan") & (ids != "Grand Total")]
            
            # Use ID pattern to verify/determine funder
            if ids.empty:
                return [], None
                
            first_id = ids.iloc[0]
            for funder, pattern in self.id_patterns.items():
                if re.match(pattern, str(first_id)):
                    suspected_funder = funder
                    break
                    
            return ids.tolist(), suspected_funder
            
        except Exception as e:
            self.logger.error(f"Error extracting advance IDs: {str(e)}")
            raise
    
    def _try_read_weekly_format(self, file_path: Path) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """Try to read a file in ACS/Vesper weekly format."""
        try:
            # First read to check format
            df = pd.read_csv(file_path)
            if 'Withdrawn per deal' not in df.columns:
                return None, None
                
            # Find the header row containing "Advance ID"
            header_row = None
            for idx, row in df.iterrows():
                if any('Advance ID' in str(val) for val in row.values):
                    header_row = idx
                    break
                    
            if header_row is None:
                return None, None
                
            # Read file again with the correct header row
            df = pd.read_csv(file_path, skiprows=header_row)
            df.columns = df.iloc[0]  # Use the first row as headers
            df = df.iloc[1:]  # Remove the header row from data
            
            # Determine if ACS or Vesper
            first_id = str(df.iloc[0]['Advance ID']).strip()
            if first_id.startswith('AC'):
                return df, "ACS"
            elif first_id.startswith('VC'):
                return df, "Vesper"
                
            return df, None
            
        except Exception as e:
            self.logger.error(f"Error reading weekly format: {str(e)}")
            return None, None
        
    def _try_read_regular_format(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Try to read a file in regular CSV format."""
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            self.logger.error(f"Error reading regular format: {str(e)}")
            return None


    def _add_new_ids_to_database(self, funder: str, new_ids: List[str], file_path: Path, portfolio: Optional[str] = None):
        """Add newly discovered advance IDs to the database."""
        try:
            if not new_ids:
                return
                
            # Read merchant names if available
            df = pd.read_csv(file_path)
            self.logger.debug(f"Reading file {file_path} for merchant names")
            
            # Find ID and merchant columns based on funder
            id_col = None
            merchant_col = None
            
            # Define column mappings for each funder
            column_mappings = {
                "ACS": {"id": "Advance ID", "merchant": "Merchant Name"},
                "Vesper": {"id": "Advance ID", "merchant": "Merchant Name"},
                "BHB": {"id": "Deal ID", "merchant": "Deal Name"},
                "Kings": {"id": "Advance ID", "merchant": "Business Name"},
                "Boom": {"id": "Advance ID", "merchant": "Business Name"},
                "EFIN": {"id": "Advance ID", "merchant": "Business Name"},
                "ClearView": {"id": "AdvanceID", "merchant": None}  # ClearView doesn't have merchant names
            }
            
            mapping = column_mappings.get(funder)
            if not mapping:
                raise ValueError(f"Unknown funder: {funder}")
                
            # Find columns (case-insensitive)
            for col in df.columns:
                if mapping["id"].lower() == col.lower():
                    id_col = col
                elif mapping["merchant"] and mapping["merchant"].lower() == col.lower():
                    merchant_col = col
                    
            if not id_col:
                raise ValueError(f"Could not find ID column for {funder}")
                
            current_time = pd.Timestamp.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                for advance_id in new_ids:
                    try:
                        merchant_name = None
                        if merchant_col:
                            # Find matching row
                            matching_row = df[df[id_col].astype(str).str.strip() == str(advance_id).strip()]
                            if not matching_row.empty:
                                merchant_name = matching_row[merchant_col].iloc[0]
                                if pd.isna(merchant_name):
                                    merchant_name = None
                                else:
                                    merchant_name = str(merchant_name).strip()
                        
                        # Insert with portfolio information
                        conn.execute('''
                            INSERT OR REPLACE INTO merchant_tracking 
                            (advance_id, funder, merchant_name, portfolio, first_seen_date, last_updated)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (advance_id, funder, merchant_name, portfolio or "Unknown", current_time, current_time))
                        
                    except Exception as e:
                        self.logger.error(f"Error adding ID {advance_id}: {str(e)}")
                        continue
                        
            self.logger.info(f"Added {len(new_ids)} new IDs to database for {funder}")
            
        except Exception as e:
            self.logger.error(f"Error adding new IDs to database: {str(e)}")

    def _lookup_ids_in_database(self, advance_ids: List[str]) -> Dict[str, List[str]]:
        """Look up advance IDs in the database and group by funder."""
        funder_matches = {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                placeholders = ','.join('?' * len(advance_ids))
                query = f'''
                    SELECT advance_id, funder 
                    FROM merchant_tracking 
                    WHERE advance_id IN ({placeholders})
                '''
                
                cursor = conn.execute(query, advance_ids)
                for row in cursor:
                    funder = row[1]
                    if funder not in funder_matches:
                        funder_matches[funder] = []
                    funder_matches[funder].append(row[0])
                    
            return funder_matches
            
        except Exception as e:
            self.logger.error(f"Error looking up IDs in database: {str(e)}")
            return {}

    def _pattern_match_ids(self, advance_ids: List[str]) -> Dict[str, List[str]]:
        """Match advance IDs against known patterns."""
        pattern_matches = {}
        
        for id_value in advance_ids:
            for funder, pattern in self.id_patterns.items():
                if re.match(pattern, str(id_value)):
                    if funder not in pattern_matches:
                        pattern_matches[funder] = []
                    pattern_matches[funder].append(id_value)
                    
        return pattern_matches

    def _verify_column_structure(self, file_path: Path, suspected_funder: str) -> float:
        """Verify column structure matches expected pattern for funder."""
        try:
            df = pd.read_csv(file_path)
            expected_columns = self.column_patterns[suspected_funder]
            
            # Count matching columns
            matches = sum(1 for col in expected_columns if col in df.columns)
            return matches / len(expected_columns)
            
        except Exception as e:
            self.logger.error(f"Error verifying column structure: {str(e)}")
            return 0.0


    def classify_funder(self, file_path: Path) -> ClassificationResult:
        """Classify a CSV file by funder."""
        try:
            # Extract advance IDs and get initial funder guess
            advance_ids, suspected_funder = self._extract_advance_ids(file_path)
            
            if not advance_ids:
                return ClassificationResult(
                    funder=None,
                    confidence=0.0,
                    new_ids=[],
                    matched_ids=[],
                    reason="No valid advance IDs found"
                )
                
            # If we have a suspected funder from file format/patterns
            if suspected_funder:
                # Verify with column structure
                column_score = self._verify_column_structure(file_path, suspected_funder)
                if column_score >= 0.7:
                    # Look up existing IDs
                    db_matches = self._lookup_ids_in_database(advance_ids)
                    matched_ids = db_matches.get(suspected_funder, [])
                    new_ids = [id_ for id_ in advance_ids if id_ not in matched_ids]
                    
                    # Add new IDs to database
                    if new_ids:
                        self._add_new_ids_to_database(suspected_funder, new_ids, file_path)
                        
                    return ClassificationResult(
                        funder=suspected_funder,
                        confidence=column_score,
                        new_ids=new_ids,
                        matched_ids=matched_ids,
                        reason=f"Format and pattern match for {suspected_funder}"
                    )
                    
            # If no clear match, fall back to database lookup
            db_matches = self._lookup_ids_in_database(advance_ids)
            if db_matches:
                best_funder = max(db_matches.items(), key=lambda x: len(x[1]))
                match_ratio = len(best_funder[1]) / len(advance_ids)
                
                if match_ratio >= 0.5:
                    matched_ids = best_funder[1]
                    new_ids = [id_ for id_ in advance_ids if id_ not in matched_ids]
                    
                    if new_ids:
                        self._add_new_ids_to_database(best_funder[0], new_ids, file_path)
                        
                    return ClassificationResult(
                        funder=best_funder[0],
                        confidence=match_ratio,
                        new_ids=new_ids,
                        matched_ids=matched_ids,
                        reason="Database match"
                    )
            
            return ClassificationResult(
                funder=None,
                confidence=0.0,
                new_ids=[],
                matched_ids=[],
                reason="Could not confidently determine funder"
            )
            
        except Exception as e:
            self.logger.error(f"Error classifying file: {str(e)}")
            return ClassificationResult(
                funder=None,
                confidence=0.0,
                new_ids=[],
                matched_ids=[],
                reason=f"Error: {str(e)}"
            )