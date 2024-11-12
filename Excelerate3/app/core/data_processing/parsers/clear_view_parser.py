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
                    except Exception as e:
                        self.logger.error(f"Error reading CSV with {encoding}: {str(e)}")
                        continue
                
                if df is None:
                    raise ValueError(f"Unable to read {file_path} with any encoding")
                
                # Add Merchant Name if missing
                if "Merchant Name" not in df.columns:
                    df["Merchant Name"] = df["AdvanceID"]
                
                all_dfs.append(df)
            
            # Combine all dataframes
            combined_df = pd.concat(all_dfs, ignore_index=True)
            self._df = combined_df
            return combined_df

        except Exception as e:
            self.logger.error(f"Error reading CSV files: {str(e)}")
            raise

    def process_data(self) -> pd.DataFrame:
        """Process the combined data from all files."""
        try:
            df = self._df.copy()

            # Convert currency columns
            df['Syn Gross Amount'] = df['Syn Gross Amount'].apply(self.currency_to_float)
            df['Syn Net Amount'] = df['Syn Net Amount'].apply(self.currency_to_float)

            # Filter out rows with zero values
            df = df[
                (df['Syn Gross Amount'] != 0) &
                (df['Syn Net Amount'] != 0)
            ]

            # Group by advance ID and merchant name
            grouped = df.groupby(['AdvanceID', 'Merchant Name']).agg({
                'Syn Gross Amount': 'sum',
                'Syn Net Amount': 'sum'
            }).reset_index()

            # Calculate fees
            grouped['Servicing Fee'] = (grouped['Syn Gross Amount'] - grouped['Syn Net Amount']).round(2)

            # Create standardized DataFrame
            processed_df = pd.DataFrame({
                "Advance ID": grouped['AdvanceID'],
                "Merchant Name": grouped['Merchant Name'],
                "Gross Payment": grouped['Syn Gross Amount'],
                "Fees": grouped['Servicing Fee'].abs(),
                "Net": grouped['Syn Net Amount']
            })

            # Remove any all-zero rows
            processed_df = processed_df[
                ~((processed_df["Gross Payment"] == 0) &
                  (processed_df["Fees"] == 0) &
                  (processed_df["Net"] == 0))
            ]

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

            return pivot, total_gross, total_net, total_fee, None

        except Exception as e:
            error_msg = f"Error processing ClearView files: {str(e)}"
            self.logger.error(error_msg)
            return None, 0, 0, 0, error_msg