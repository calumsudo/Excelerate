from pathlib import Path
import pandas as pd
from typing import Tuple, Optional, Dict
from .base_parser import BaseParser

class BHBParser(BaseParser):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.funder_name = "BHB"
        self.required_columns = [
            "Deal ID",
            "Deal Name",
            "Participator Gross Amount",
            "Non Qualifying Collections",
            "Total Reversals",
            "Fee",
            "Res. Commission",
            "Net Payment Amount",
            "Balance"
        ]
        self.column_types = {
            "Deal ID": str,
            "Deal Name": str,
            "Participator Gross Amount": float,
            "Fee": float,
            "Net Payment Amount": float
        }

    def currency_to_float(self, value: any) -> float:
        """Convert currency string to float."""
        if isinstance(value, str):
            value = (
                value.replace("$", "")
                .replace(",", "")
                .replace("(", "-")
                .replace(")", "")
                .strip()
            )
        return float(value)

    def validate_format(self) -> Tuple[bool, str]:
        """Override validate_format to handle original column names"""
        try:
            # Read the file first
            if self._df is None:
                if self.file_path.suffix.lower() == '.xlsx':
                    self._df = pd.read_excel(self.file_path, sheet_name="Sheet1")
                elif self.file_path.suffix.lower() == '.csv':
                    self._df = pd.read_csv(self.file_path, encoding='utf-8')
                else:
                    return False, "Unsupported file format. Please provide an XLSX or CSV file."

            # Validate original columns
            missing_columns = [col for col in self.required_columns 
                             if col not in self._df.columns]
            if missing_columns:
                return False, f"Missing columns: {', '.join(missing_columns)}"

            return True, ""

        except Exception as e:
            return False, str(e)

    def read_csv(self) -> pd.DataFrame:
        """Process the data after validation"""
        try:
            df = self._df.copy()
            
            # Filter out non-numeric Deal IDs
            df = df[pd.to_numeric(df["Deal ID"], errors="coerce").notnull()]

            # Convert currency columns to float
            df["Participator Gross Amount"] = df["Participator Gross Amount"].apply(self.currency_to_float)
            df["Net Payment Amount"] = df["Net Payment Amount"].apply(self.currency_to_float)
            df["Fee"] = df["Fee"].apply(self.currency_to_float)

            # Create standardized DataFrame
            processed_df = pd.DataFrame({
                "Advance ID": df["Deal ID"],
                "Merchant Name": df["Deal Name"],
                "Gross Payment": df["Participator Gross Amount"],
                "Fees": df["Fee"].abs(),  # Use absolute value of Fee
                "Net": df["Net Payment Amount"]
            })

            self._df = processed_df
            return processed_df

        except Exception as e:
            self.logger.error(f"Error processing BHB file: {str(e)}")
            raise

    def process(self) -> Tuple[pd.DataFrame, float, float, float, Optional[str]]:
        try:
            # Validate format
            is_valid, error_msg = self.validate_format()
            if not is_valid:
                return None, 0, 0, 0, error_msg

            # Process the data
            self.read_csv()

            # Sum the values directly from the processed DataFrame
            total_gross = self._df["Gross Payment"].sum()
            total_net = self._df["Net"].sum()
            total_fee = self._df["Fees"].sum()

            # Create pivot table using the base class method
            pivot = self.create_pivot_table(
                df=self._df,
                gross_col="Gross Payment",
                net_col="Net",
                fee_col="Fees",
                index=["Advance ID", "Merchant Name"]
            )

            return pivot, total_gross, total_net, total_fee, None

        except Exception as e:
            error_msg = f"Error processing BHB file: {str(e)}"
            self.logger.error(error_msg)
            return None, 0, 0, 0, error_msg