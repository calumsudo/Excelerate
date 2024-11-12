# core/data_processing/parsers/clear_view_parser.py
from pathlib import Path
import pandas as pd
from typing import Tuple, Optional, Dict, List, Union
from .base_parser import BaseParser

class ClearViewParser(BaseParser):
    def __init__(self, file_path: Union[Path, List[Path]]):
        """
        Initialize the ClearView parser with one or more file paths.
        
        Args:
            file_path: Either a single Path or a list of Paths to ClearView reports
        """
        # Store all file paths
        self.all_file_paths = [Path(file_path)] if isinstance(file_path, (str, Path)) else [Path(p) for p in file_path]
        
        # Initialize base class with first file path to maintain compatibility
        super().__init__(self.all_file_paths[0])
        
        self.funder_name = "ClearView"
        self.required_columns = [
            "Last Merchant Cleared Date",
            "Advance Status",
            "AdvanceID",
            "Frequency",
            "Repayment Type",
            "Draft Amount",
            "Return Code",
            "Return Date",
            "Syn Gross Amount",
            "Syn Net Amount",
            "Syn Cleared Date",
            "Syndicated Amt",
            "Syndicate Purchase Price",
            "Syndicate Net RTR Remain"
        ]
        self.column_types = {
            'AdvanceID': str,
            'Syn Gross Amount': float,
            'Syn Net Amount': float
        }

        self._combined_df = None

        # Log initialization
        self.logger.info(f"Initializing ClearView parser with {len(self.all_file_paths)} files")
        for path in self.all_file_paths:
            self.logger.info(f"File to process: {path}")
        
    @property
    def file_names(self) -> str:
        """Return comma-separated list of file names for logging."""
        return ", ".join(f.name for f in self.all_file_paths)
    
    @property
    def name(self) -> str:
        """Return name property for compatibility with test framework."""
        return self.all_file_paths[0].name

    def currency_to_float(self, value: any) -> float:
        """Convert currency string to float."""
        if pd.isna(value):
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove currency symbols, commas, and handle parentheses
            value = (
                value.replace("$", "")
                .replace(",", "")
                .replace("(", "-")
                .replace(")", "")
                .replace('"', "")
                .strip()
            )
            try:
                return float(value) if value else 0.0
            except ValueError:
                return 0.0
        return 0.0

    def read_csv(self) -> pd.DataFrame:
        """Read and combine all provided CSV files."""
        try:
            all_dfs = []
            
            for file_path in self.all_file_paths:
                self.logger.info(f"Processing file: {file_path}")
                
                if not file_path.exists():
                    self.logger.error(f"File does not exist: {file_path}")
                    continue
                    
                encodings_to_try = [
                    self.detect_encoding(),
                    'utf-8',
                    'cp1252',
                    'iso-8859-1'
                ]
                
                df = None
                for encoding in encodings_to_try:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        self.logger.info(f"Successfully read file with {encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        self.logger.error(f"Error reading CSV with {encoding}: {str(e)}")
                        continue
                
                if df is None:
                    self.logger.error(f"Unable to read {file_path} with any encoding")
                    continue

                # Log unique status values
                unique_statuses = df['Advance Status'].unique()
                self.logger.info(f"Found status values: {unique_statuses}")
                
                # Verify required columns
                missing_columns = [col for col in self.required_columns if col not in df.columns]
                if missing_columns:
                    self.logger.error(f"Missing required columns in {file_path}: {missing_columns}")
                    continue

                # Convert AdvanceID to string immediately after reading
                df['AdvanceID'] = df['AdvanceID'].astype(str)
                
                # Convert amount columns to float
                df['Syn Gross Amount'] = df['Syn Gross Amount'].apply(self.currency_to_float)
                df['Syn Net Amount'] = df['Syn Net Amount'].apply(self.currency_to_float)
                
                # Filter for valid records (more permissive status check)
                valid_statuses = ['Funded - In Repayment', 'In Repayment', 'Funded']
                df = df[
                    df['Advance Status'].str.contains('|'.join(valid_statuses), case=False, na=False) |
                    (df['Syn Gross Amount'] > 0)
                ]
                
                if len(df) == 0:
                    self.logger.warning(f"No valid records found in {file_path} after filtering")
                    # Log some sample rows from original data
                    self.logger.info("Sample of original data:")
                    self.logger.info(df.head().to_string())
                    continue
                
                self.logger.info(f"Found {len(df)} valid records in {file_path}")
                
                # Log some statistics
                self.logger.info("Summary of amounts:")
                self.logger.info(f"Total Syn Gross Amount: {df['Syn Gross Amount'].sum():,.2f}")
                self.logger.info(f"Total Syn Net Amount: {df['Syn Net Amount'].sum():,.2f}")
                
                all_dfs.append(df)
            
            if not all_dfs:
                raise ValueError("No valid data found in any of the provided files")
            
            # Combine all dataframes
            self._combined_df = pd.concat(all_dfs, ignore_index=True)
            self.logger.info(f"Combined DataFrame has {len(self._combined_df)} rows")
            
            # Log combined data statistics
            self.logger.info("Combined data summary:")
            self.logger.info(f"Total records: {len(self._combined_df)}")
            self.logger.info(f"Unique AdvanceIDs: {len(self._combined_df['AdvanceID'].unique())}")
            self.logger.info(f"Total Syn Gross Amount: {self._combined_df['Syn Gross Amount'].sum():,.2f}")
            
            # Deduplicate based on unique identifiers and date
            self._combined_df = self._combined_df.sort_values('Last Merchant Cleared Date').drop_duplicates(
                subset=['AdvanceID', 'Syn Cleared Date', 'Syn Gross Amount', 'Syn Net Amount'],
                keep='last'
            )
            
            self.logger.info(f"After deduplication: {len(self._combined_df)} rows")
            self._df = self._combined_df
            return self._combined_df

        except Exception as e:
            self.logger.error(f"Error reading CSV files: {str(e)}")
            raise

    def validate_format(self) -> Tuple[bool, str]:
        """Validate format of all provided files."""
        try:
            for file_path in self.all_file_paths:
                encodings_to_try = [
                    self.detect_encoding(),
                    'utf-8',
                    'cp1252',
                    'iso-8859-1'
                ]
                
                df = None
                for encoding in encodings_to_try:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    return False, f"Unable to read {file_path} with any encoding"
                
                # Check for required columns
                missing_columns = [col for col in self.required_columns 
                                if col not in df.columns]
                if missing_columns:
                    return False, f"Missing columns in {file_path.name}: {', '.join(missing_columns)}"

            return True, ""

        except Exception as e:
            return False, str(e)

    def process(self) -> Tuple[pd.DataFrame, float, float, float, Optional[str]]:
        try:
            # First validate format
            is_valid, error_msg = self.validate_format()
            if not is_valid:
                return None, 0, 0, 0, error_msg

            # Explicitly read CSV files if not already done
            if self._df is None:
                self.read_csv()
                
            if self._df is None:  # If still None after reading, there's an error
                return None, 0, 0, 0, "Failed to read CSV files"

            # Process the data
            processed_df = self.process_data()
            if processed_df is None:
                return None, 0, 0, 0, "Failed to process data"

            # Store processed data
            self._df = processed_df

            # Calculate totals before pivot
            total_gross = processed_df["Gross Payment"].sum()
            total_net = processed_df["Net"].sum()
            total_fee = processed_df["Fees"].sum()

            # Create pivot table
            pivot = self.create_pivot_table(
                df=processed_df,
                gross_col="Gross Payment",
                net_col="Net",
                fee_col="Fees",
                index=["Advance ID", "Merchant Name"]
            )

            return pivot, total_gross, total_net, total_fee, None

        except Exception as e:
            error_msg = f"Error processing ClearView files: {str(e)}"
            self.logger.error(error_msg)
            return None, 0, 0, 0, error_msg

    def process_data(self) -> pd.DataFrame:
        """Process the combined data from all files."""
        try:
            if self._df is None:
                raise ValueError("No data available to process")
                
            df = self._df.copy()
            self.logger.info(f"Starting data processing with {len(df)} rows")

            # First filter out NaN and invalid values from AdvanceID
            valid_id_mask = (
                df['AdvanceID'].notna() & 
                (df['AdvanceID'] != '') & 
                (df['AdvanceID'].astype(str) != 'nan') &
                (~df['AdvanceID'].astype(str).str.contains(r'^\s*$', na=True))
            )
            df = df[valid_id_mask]

            # Now convert AdvanceID to clean string format
            def clean_advance_id(x):
                try:
                    # Remove any commas and spaces
                    cleaned = str(x).replace(',', '').replace(' ', '')
                    # Convert to float first to handle scientific notation
                    float_val = float(cleaned)
                    # Convert to int to remove decimal
                    int_val = int(float_val)
                    # Return as string
                    return str(int_val)
                except (ValueError, TypeError):
                    return None

            df['AdvanceID'] = df['AdvanceID'].apply(clean_advance_id)
            
            # Remove rows where clean_advance_id returned None
            df = df[df['AdvanceID'].notna()]
            
            # Remove the totals row
            df = df[~(
                df['Syn Gross Amount'].astype(str).str.contains('Total', na=False) |
                df['Syn Net Amount'].astype(str).str.contains('Total', na=False)
            )]
            
            self.logger.info(f"After removing invalid IDs and totals: {len(df)} rows")

            # Ensure amounts are numeric, removing any currency formatting
            for col in ['Syn Gross Amount', 'Syn Net Amount']:
                df[col] = pd.to_numeric(
                    df[col].astype(str).replace('[\$,]', '', regex=True),
                    errors='coerce'
                )

            # Filter out zero amounts and NaN values
            non_zero_mask = (
                (df['Syn Gross Amount'] != 0) & 
                (df['Syn Net Amount'] != 0) &
                df['Syn Gross Amount'].notna() &
                df['Syn Net Amount'].notna()
            )
            df = df[non_zero_mask]
            self.logger.info(f"After filtering zeros: {len(df)} rows")

            # Group by advance ID
            grouped = df.groupby(['AdvanceID'], as_index=False).agg({
                'Advance Status': 'first',
                'Syn Gross Amount': 'sum',
                'Syn Net Amount': 'sum'
            })
            
            # Calculate fees
            grouped['Fees'] = (grouped['Syn Gross Amount'] - grouped['Syn Net Amount']).abs().round(2)

            # Create standardized DataFrame
            processed_df = pd.DataFrame({
                "Advance ID": grouped['AdvanceID'],
                "Merchant Name": grouped['AdvanceID'],
                "Gross Payment": grouped['Syn Gross Amount'],
                "Net": grouped['Syn Net Amount'],
                "Fees": grouped['Fees']
            })

            # Remove any remaining all-zero rows
            processed_df = processed_df[
                ~((processed_df["Gross Payment"] == 0) &
                (processed_df["Net"] == 0) &
                (processed_df["Fees"] == 0))
            ]

            # Log final totals
            self.logger.info("Final totals:")
            self.logger.info(f"Total Gross: {processed_df['Gross Payment'].sum():,.2f}")
            self.logger.info(f"Total Net: {processed_df['Net'].sum():,.2f}")
            self.logger.info(f"Total Fees: {processed_df['Fees'].sum():,.2f}")

            return processed_df

        except Exception as e:
            self.logger.error(f"Error during processing: {str(e)}")
            raise