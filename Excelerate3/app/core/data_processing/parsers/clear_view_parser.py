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

    def process_data(self) -> pd.DataFrame:
        """Process the combined data from all files."""
        try:
            df = self._df.copy()
            self.logger.info(f"Starting data processing with {len(df)} rows")

            # Print sample data before processing
            self.logger.info("Sample data before processing:")
            self.logger.info(df[['AdvanceID', 'Syn Gross Amount', 'Syn Net Amount']].head().to_string())

            # Filter out rows with zero values
            non_zero_mask = (df['Syn Gross Amount'] != 0) & (df['Syn Net Amount'] != 0)
            df = df[non_zero_mask]
            self.logger.info(f"After filtering zeros: {len(df)} rows")

            # Group by advance ID and sum the amounts
            grouped = df.groupby(['AdvanceID'], as_index=False).agg({
                'Advance Status': 'first',  # Keep the first status
                'Syn Gross Amount': 'sum',
                'Syn Net Amount': 'sum'
            })
            self.logger.info(f"After grouping: {len(grouped)} rows")

            # Calculate fees
            grouped['Servicing Fee'] = (grouped['Syn Gross Amount'] - grouped['Syn Net Amount']).round(2)

            # Log grouped data
            self.logger.info("Grouped data summary:")
            self.logger.info(grouped.describe().to_string())

            # Create standardized DataFrame
            processed_df = pd.DataFrame({
                "Advance ID": grouped['AdvanceID'],
                "Merchant Name": grouped['AdvanceID'],  # Use AdvanceID as Merchant Name since it's missing in the data
                "Gross Payment": grouped['Syn Gross Amount'],
                "Fees": grouped['Servicing Fee'].abs(),
                "Net": grouped['Syn Net Amount']
            })

            # Remove any remaining zero rows
            processed_df = processed_df[
                ~((processed_df["Gross Payment"] == 0) &
                  (processed_df["Fees"] == 0) &
                  (processed_df["Net"] == 0))
            ]
            self.logger.info(f"Final processed DataFrame has {len(processed_df)} rows")

            # Log final totals
            self.logger.info("Final totals:")
            self.logger.info(f"Total Gross: {processed_df['Gross Payment'].sum():,.2f}")
            self.logger.info(f"Total Net: {processed_df['Net'].sum():,.2f}")
            self.logger.info(f"Total Fees: {processed_df['Fees'].sum():,.2f}")

            self._df = processed_df
            return processed_df

        except Exception as e:
            self.logger.error(f"Error during processing: {str(e)}")
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
            # First validate format of all files
            is_valid, error_msg = self.validate_format()
            if not is_valid:
                return None, 0, 0, 0, error_msg

            # Read and combine all files
            self.read_csv()
            
            # Process the combined data
            self.process_data()

            # Create pivot table
            pivot = self.create_pivot_table(
                df=self._df,
                gross_col="Gross Payment",
                net_col="Net",
                fee_col="Fees",
                index=["Advance ID", "Merchant Name"]
            )

            # Calculate totals
            total_gross = round(self._df["Gross Payment"].sum(), 2)
            total_net = round(self._df["Net"].sum(), 2)
            total_fee = round(self._df["Fees"].sum(), 2)

            self.logger.info(f"Processed {len(self._df)} records with totals: "
                           f"Gross=${total_gross:,.2f}, Net=${total_net:,.2f}")

            return pivot, total_gross, total_net, total_fee, None

        except Exception as e:
            error_msg = f"Error processing ClearView files: {str(e)}"
            self.logger.error(error_msg)
            return None, 0, 0, 0, error_msg