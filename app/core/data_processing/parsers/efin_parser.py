from pathlib import Path
import pandas as pd
from typing import Tuple, Optional
from .base_parser import BaseParser


class EfinParser(BaseParser):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.funder_name = "EFIN"
        self.required_columns = [
            "Funding Date",
            "Advance ID",
            "Business Name",
            "Advance Status",
            "Payable Amt (Gross)",
            "Servicing Fee $",
            "Payable Amt (Net)",
            "Payable Status",  # Added this required column
        ]
        self.column_types = {
            "Advance ID": str,
            "Business Name": str,
            "Payable Amt (Gross)": float,
            "Servicing Fee $": float,
            "Payable Amt (Net)": float,
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
            self.logger.info("Reading EFIN CSV file...")

            # Try different encodings
            encodings_to_try = ["utf-8", "cp1252", "iso-8859-1"]
            df = None

            for encoding in encodings_to_try:
                try:
                    df = pd.read_csv(self.file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                raise ValueError("Unable to read file with any supported encoding")

            self.logger.info(f"Found {len(df)} rows in file")

            # Convert Advance ID to string immediately
            df["Advance ID"] = df["Advance ID"].astype(str)

            self._df = df
            return df

        except Exception as e:
            self.logger.error(f"Error reading CSV: {str(e)}")
            raise

    def process_data(self) -> pd.DataFrame:
        """Process EFIN data."""
        try:
            if self._df is None:
                raise ValueError("No data available to process")

            df = self._df.copy()

            # Filter for valid transactions
            valid_statuses = [
                "Funded - In Repayment",
                "FUNDED - ISSUE CORRECTED",
                "FUNDED - MPI",
            ]
            status_mask = (
                df["Advance Status"]
                .str.upper()
                .isin([s.upper() for s in valid_statuses])
            )
            df = df[status_mask]

            self.logger.info(f"Found {len(df)} rows with valid status")

            # Clean Advance ID - ensure it's a string and remove any whitespace
            df["Advance ID"] = df["Advance ID"].astype(str).str.strip()

            # Convert currency columns to numeric
            for col in ["Payable Amt (Gross)", "Servicing Fee $", "Payable Amt (Net)"]:
                df[col] = df[col].apply(self.currency_to_float)

            # Group by Advance ID and Business Name to get totals
            grouped = df.groupby(["Advance ID", "Business Name"], as_index=False).agg(
                {
                    "Payable Amt (Net)": "sum",
                    "Servicing Fee $": "sum",
                    "Payable Amt (Gross)": "sum",
                }
            )

            # Round all amounts to 2 decimal places
            for col in ["Payable Amt (Net)", "Servicing Fee $", "Payable Amt (Gross)"]:
                grouped[col] = grouped[col].round(2)

            # Create standardized DataFrame with correct column mapping
            processed_df = pd.DataFrame(
                {
                    "Advance ID": grouped["Advance ID"],
                    "Merchant Name": grouped["Business Name"],
                    "Sum of Syn Net Amount": grouped["Payable Amt (Net)"],
                    "Sum of Syn Gross Amount": grouped["Payable Amt (Gross)"],
                    "Total Servicing Fee": grouped[
                        "Servicing Fee $"
                    ].abs(),  # Ensure fees are positive
                }
            )

            # Log processing details
            self.logger.info(f"Processed {len(processed_df)} unique advances")
            self.logger.info(
                f"Total Gross: ${processed_df['Sum of Syn Gross Amount'].sum():,.2f}"
            )
            self.logger.info(
                f"Total Net: ${processed_df['Sum of Syn Net Amount'].sum():,.2f}"
            )
            self.logger.info(
                f"Total Fees: ${processed_df['Total Servicing Fee'].sum():,.2f}"
            )

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
                index=["Advance ID", "Merchant Name"],
            )

            return pivot, total_gross, total_net, total_fee, None

        except Exception as e:
            error_msg = f"Error processing EFIN file: {str(e)}"
            self.logger.error(error_msg)
            return None, 0, 0, 0, error_msg
