from pathlib import Path
import pandas as pd
from typing import Tuple, Optional, Dict
from .base_parser import BaseParser

class EfinParser(BaseParser):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.funder_name = None
        self.required_columns = [
            'Funding Date',
            'Advance ID', 
            'Business Name',
            'Advance Status',
            'Payable Amt (Gross)',
            'Servicing Fee $',
            'Payable Amt (Net)'
        ]
        self.column_types = {
            'Advance ID': str,
            'Business Name': str,
            'Payable Amt (Gross)': float,
            'Servicing Fee $': float,
            'Payable Amt (Net)': float
        }
        
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
        """Read and perform initial processing of the CSV file"""
        try:
            print("\nReading CSV file...")
            # Read CSV file
            df = pd.read_csv(self.file_path, encoding='utf-8')
            print(f"Found {len(df)} rows in file")
            
            self._df = df
            return df

        except Exception as e:
            print(f"\nError reading CSV: {str(e)}")
            raise

    def process_data(self) -> pd.DataFrame:
        """Process EFIN data."""
        try:
            if self._df is None:
                raise ValueError("No data available to process")

            df = self._df.copy()

            # Filter for valid transactions
            df = df[df['Advance Status'] == "Funded - In Repayment"]

            # Convert currency columns to numeric
            for col in ['Payable Amt (Gross)', 'Servicing Fee $', 'Payable Amt (Net)']:
                df[col] = pd.to_numeric(
                    df[col].astype(str).replace(r'[\$,]', '', regex=True),
                    errors='coerce'
                )

            # Group by Advance ID and Business Name to get totals
            grouped = df.groupby(['Advance ID', 'Business Name'], as_index=False).agg({
                'Payable Amt (Net)': 'sum',
                'Servicing Fee $': 'sum',
                'Payable Amt (Gross)': 'sum'
            })

            # Round all amounts to 2 decimal places
            for col in ['Payable Amt (Net)', 'Servicing Fee $', 'Payable Amt (Gross)']:
                grouped[col] = grouped[col].round(2)

            # Create standardized DataFrame with correct column mapping
            processed_df = pd.DataFrame({
                "Advance ID": grouped['Advance ID'],
                "Merchant Name": grouped['Business Name'],
                "Sum of Syn Net Amount": grouped['Payable Amt (Net)'],
                "Sum of Syn Gross Amount": grouped['Payable Amt (Gross)'],
                "Total Servicing Fee": grouped['Servicing Fee $'].abs()  # Ensure fees are positive
            })

            # Log the totals for verification
            self.logger.info("Final totals:")
            self.logger.info(f"Total Net: {processed_df['Sum of Syn Net Amount'].sum():,.2f}")
            self.logger.info(f"Total Fee: {processed_df['Total Servicing Fee'].sum():,.2f}")
            self.logger.info(f"Total Gross: {processed_df['Sum of Syn Gross Amount'].sum():,.2f}")

            return processed_df

        except Exception as e:
            self.logger.error(f"Error processing EFIN data: {str(e)}")
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

            # Create pivot table with standardized column names
            pivot = self.create_pivot_table(
                df=processed_df,
                gross_col="Sum of Syn Gross Amount",
                net_col="Sum of Syn Net Amount",
                fee_col="Total Servicing Fee",
                index=["Advance ID", "Merchant Name"]
            )

            return pivot, total_gross, total_net, total_fee, None

        except Exception as e:
            error_msg = f"Error processing {self.funder_name or 'EFIN'} file: {str(e)}"
            self.logger.error(error_msg)
            return None, 0, 0, 0, error_msg