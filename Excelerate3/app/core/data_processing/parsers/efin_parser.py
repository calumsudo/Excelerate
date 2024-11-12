from pathlib import Path
import pandas as pd
from typing import Tuple, Optional, Dict
from .base_parser import BaseParser

class EfinParser(BaseParser):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.funder_name = "EFIN"
        self.required_columns = [
            'Funding Date',
            'Advance ID', 
            'Business Name',
            'Advance Status',
            'Debit Amount',
            'Debit Date',
            'Last Merchant Cleared Date',
            'Syndicators Name',
            'Payable Amt (Gross)',
            'Servicing Fee $',
            'Payable Amt (Net)',
            'Payable Cleared Date',
            'Freq',
            'Repay Type'
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
        """Process the data after validation"""
        try:
            print("\nProcessing CSV data...")
            df = self._df.copy()

            # Filter for specific payable records
            df = df[df['Advance Status'] == "Funded - In Repayment"]
            print(f"Rows after status filter: {len(df)}")

            # Convert currency columns
            print("\nConverting currency columns...")
            df['Payable Amt (Gross)'] = df['Payable Amt (Gross)'].apply(self.currency_to_float)
            df['Servicing Fee $'] = df['Servicing Fee $'].apply(self.currency_to_float)
            df['Payable Amt (Net)'] = df['Payable Amt (Net)'].apply(self.currency_to_float)

            # Group by Business Name and Advance ID
            print("\nGrouping transactions...")
            grouped = df.groupby(['Business Name', 'Advance ID']).agg({
                'Payable Amt (Gross)': 'sum',
                'Servicing Fee $': 'sum',
                'Payable Amt (Net)': 'sum'
            }).reset_index()

            print(f"Rows after grouping: {len(grouped)}")

            # Create standardized DataFrame
            processed_df = pd.DataFrame({
                "Advance ID": grouped['Advance ID'],
                "Merchant Name": grouped['Business Name'],
                "Gross Payment": grouped['Payable Amt (Gross)'],
                "Fees": grouped['Servicing Fee $'].abs(),
                "Net": grouped['Payable Amt (Net)']
            })

            # Remove any all-zero rows
            processed_df = processed_df[
                ~((processed_df["Gross Payment"] == 0) &
                  (processed_df["Fees"] == 0) &
                  (processed_df["Net"] == 0))
            ]

            print("\nFinal dataframe totals:")
            print(f"Total Gross: ${processed_df['Gross Payment'].sum():,.2f}")
            print(f"Total Fee: ${processed_df['Fees'].sum():,.2f}")
            print(f"Total Net: ${processed_df['Net'].sum():,.2f}")

            self._df = processed_df
            return processed_df

        except Exception as e:
            print(f"\nError during processing: {str(e)}")
            raise

    def process(self) -> Tuple[pd.DataFrame, float, float, float, Optional[str]]:
        try:
            # First read the file
            self.read_csv()
            
            # Then validate format
            is_valid, error_msg = self.validate_format()
            if not is_valid:
                return None, 0, 0, 0, error_msg

            # Process the data
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
            total_gross = self._df["Gross Payment"].sum()
            total_net = self._df["Net"].sum()
            total_fee = self._df["Fees"].sum()

            # Round totals
            total_gross = round(total_gross, 2)
            total_net = round(total_net, 2)
            total_fee = round(total_fee, 2)

            print("\nFinal totals:")
            print(f"Total Gross: ${total_gross:,.2f}")
            print(f"Total Fee: ${total_fee:,.2f}")
            print(f"Total Net: ${total_net:,.2f}")

            return pivot, total_gross, total_net, total_fee, None

        except Exception as e:
            error_msg = f"Error processing EFIN file: {str(e)}"
            print(f"\nError in process method: {error_msg}")
            return None, 0, 0, 0, error_msg