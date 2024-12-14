# app/core/data_processing/parsers/kings_boom_parser.py

from pathlib import Path
import pandas as pd
from typing import Tuple, Optional, Dict
from .base_parser import BaseParser

class KingsBoomParser(BaseParser):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.funder_name = None
        self.required_columns = [
            "Funding Date", "Advance ID", "Business Name",
            "Payable Amt (Gross)", "Servicing Fee $", "Payable Amt (Net)"
        ]
        self.column_types = {
            "Advance ID": str,
            "Business Name": str,
            "Payable Amt (Gross)": float,
            "Servicing Fee $": float,
            "Payable Amt (Net)": float
        }

    def process_data(self) -> pd.DataFrame:
        """Process Kings/Boom data."""
        try:
            if self._df is None:
                raise ValueError("No data available to process")

            df = self._df.copy()

            # Clean and standardize the Advance ID
            def clean_advance_id(x):
                try:
                    if pd.isna(x) or str(x).strip() == '':
                        return None
                    # Remove any non-numeric characters and convert to string
                    numeric = ''.join(c for c in str(x) if c.isdigit())
                    if not numeric:
                        return None
                    return numeric
                except (ValueError, TypeError):
                    return None

            df['Advance ID'] = df['Advance ID'].apply(clean_advance_id)
            df = df[df['Advance ID'].notna()]

            # Convert amount columns to numeric, handling currency formatting and negative numbers
            for col in ['Payable Amt (Gross)', 'Servicing Fee $', 'Payable Amt (Net)']:
                # Remove currency symbols and commas
                df[col] = df[col].astype(str).replace(r'[\$,]', '', regex=True)
                # Convert parentheses to negative signs
                df[col] = df[col].str.replace(r'\((.*)\)', r'-\1', regex=True)
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).round(2)

            # Filter out rows where both amounts are zero
            non_zero_mask = (
                (df['Payable Amt (Gross)'] != 0) | 
                (df['Payable Amt (Net)'] != 0)
            )
            df = df[non_zero_mask]

            # Create final DataFrame with standardized column names
            processed_df = pd.DataFrame({
                "Advance ID": df["Advance ID"],
                "Merchant Name": df["Business Name"],  # Map Business Name to Merchant Name
                "Sum of Syn Net Amount": df["Payable Amt (Net)"],
                "Sum of Syn Gross Amount": df["Payable Amt (Gross)"],
                "Total Servicing Fee": df["Servicing Fee $"].abs()  # Ensure fees are positive
            })

            # Log processing details
            self.logger.info(f"Processed {len(processed_df)} rows")
            self.logger.info(f"Total Gross: {processed_df['Sum of Syn Gross Amount'].sum():,.2f}")
            self.logger.info(f"Total Net: {processed_df['Sum of Syn Net Amount'].sum():,.2f}")
            self.logger.info(f"Total Fees: {processed_df['Total Servicing Fee'].sum():,.2f}")

            return processed_df

        except Exception as e:
            self.logger.error(f"Error processing data: {str(e)}")
            raise

    def process(self) -> Tuple[pd.DataFrame, float, float, float, Optional[str]]:
        try:
            # Validate format
            is_valid, error_msg = self.validate_format()
            if not is_valid:
                return None, 0, 0, 0, error_msg

            # Ensure data is loaded
            if self._df is None:
                self.read_csv()

            if self._df is None:
                return None, 0, 0, 0, "Failed to read CSV file"

            # Process the data
            processed_df = self.process_data()
            if processed_df is None:
                return None, 0, 0, 0, "Failed to process data"

            # Calculate totals
            total_gross = processed_df["Sum of Syn Gross Amount"].sum()
            total_net = processed_df["Sum of Syn Net Amount"].sum()
            total_fee = processed_df["Total Servicing Fee"].sum()

            # Create pivot table using standardized column names
            pivot = self.create_pivot_table(
                df=processed_df,
                gross_col="Sum of Syn Gross Amount",
                net_col="Sum of Syn Net Amount",
                fee_col="Total Servicing Fee",
                index=["Advance ID", "Merchant Name"]
            )

            return pivot, total_gross, total_net, total_fee, None

        except Exception as e:
            error_msg = f"Error processing {self.funder_name or 'Kings/Boom'} file: {str(e)}"
            self.logger.error(error_msg)
            return None, 0, 0, 0, error_msg