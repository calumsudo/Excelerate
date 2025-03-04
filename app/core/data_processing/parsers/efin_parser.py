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
            "Payable Status",
        ]
        self.column_types = {
            "Advance ID": str,
            "Business Name": str,
            "Payable Amt (Gross)": float,
            "Servicing Fee $": float,
            "Payable Amt (Net)": float,
        }

        # Add debugging counters
        self.debug_stats = {
            "total_rows": 0,
            "rows_after_status_filter": 0,
            "rows_after_amount_filter": 0,
            "invalid_advance_ids": 0,
            "zero_amount_rows": 0,
            "status_distribution": {},
            "processing_errors": [],
        }

    def currency_to_float(self, value: any) -> float:
        """Convert currency string to float with debug logging."""
        try:
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
                    self.debug_stats["processing_errors"].append(
                        f"Failed to convert value to float: {value}"
                    )
                    return 0.0
            return 0.0
        except Exception as e:
            self.debug_stats["processing_errors"].append(
                f"Error in currency_to_float: {str(e)} for value: {value}"
            )
            return 0.0

    def read_csv(self) -> pd.DataFrame:
        """Read and perform initial processing of the CSV file with enhanced debugging"""
        try:
            self.logger.info("Reading EFIN CSV file...")

            # Try different encodings
            encodings_to_try = ["utf-8", "cp1252", "iso-8859-1"]
            df = None

            for encoding in encodings_to_try:
                try:
                    df = pd.read_csv(self.file_path, encoding=encoding)
                    self.logger.info(f"Successfully read file with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                raise ValueError("Unable to read file with any supported encoding")

            # Update debug stats
            self.debug_stats["total_rows"] = len(df)
            self.debug_stats["status_distribution"] = (
                df["Advance Status"].value_counts().to_dict()
            )

            # Log initial data statistics
            self.logger.info(f"Initial row count: {len(df)}")
            self.logger.info("Status distribution:")
            for status, count in self.debug_stats["status_distribution"].items():
                self.logger.info(f"  {status}: {count}")

            self._df = df
            return df

        except Exception as e:
            self.logger.error(f"Error reading CSV: {str(e)}")
            raise

    def process_data(self) -> pd.DataFrame:
        """
        Process EFIN data with fixes for White Rabbit portfolio.
        Includes enhanced debugging and less restrictive filtering.
        """
        try:
            if self._df is None:
                raise ValueError("No data available to process")

            df = self._df.copy()

            # Log initial state
            self.logger.info(f"Starting processing with {len(df)} rows")
            self.debug_stats["total_rows"] = len(df)

            # Log status distribution before filtering
            status_counts = df["Advance Status"].value_counts()
            self.logger.info("\nInitial Status Distribution:")
            for status, count in status_counts.items():
                self.logger.info(f"  {status}: {count}")

            # Remove any completely empty rows
            df = df.dropna(how="all")
            self.logger.info(f"Rows after removing empty rows: {len(df)}")

            # Clean and validate Advance ID
            df["Advance ID"] = df["Advance ID"].astype(str).str.strip()
            invalid_ids = df[df["Advance ID"].str.len() == 0]["Advance ID"]
            self.debug_stats["invalid_advance_ids"] = len(invalid_ids)

            if not invalid_ids.empty:
                self.logger.warning(f"Found {len(invalid_ids)} invalid Advance IDs")

            df = df[df["Advance ID"].str.len() > 0]
            self.logger.info(f"Rows after Advance ID validation: {len(df)}")

            # Convert currency columns with detailed logging
            currency_columns = [
                "Payable Amt (Gross)",
                "Servicing Fee $",
                "Payable Amt (Net)",
            ]
            for col in currency_columns:
                # Store original values for comparison
                original_values = df[col].copy()
                df[col] = df[col].apply(self.currency_to_float)

                # Log significant changes
                significant_changes = (
                    (df[col] != original_values)
                    & (original_values.notna())
                    & (df[col] != 0)
                )

                if significant_changes.any():
                    self.logger.info(f"\nSignificant changes in {col}:")
                    changed_rows = df[significant_changes]
                    for idx, row in changed_rows.iterrows():
                        self.logger.info(
                            f"  Advance ID {row['Advance ID']}: "
                            f"{original_values[idx]} -> {row[col]}"
                        )

            # Group by Advance ID only (not Business Name)
            # This matches Excel's pivot table behavior
            grouped = df.groupby("Advance ID", as_index=False).agg(
                {
                    "Business Name": "first",  # Take first business name
                    "Payable Amt (Net)": "sum",
                    "Servicing Fee $": "sum",
                    "Payable Amt (Gross)": "sum",
                    "Advance Status": lambda x: ", ".join(
                        sorted(set(x))
                    ),  # Keep track of all statuses
                }
            )

            # Round all amounts to 2 decimal places
            for col in ["Payable Amt (Net)", "Servicing Fee $", "Payable Amt (Gross)"]:
                grouped[col] = grouped[col].round(2)

            # Create standardized DataFrame
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

            # Log processing summary
            self.logger.info("\nProcessing Summary:")
            self.logger.info(f"Initial row count: {self.debug_stats['total_rows']}")
            self.logger.info(
                f"Invalid Advance IDs found: {self.debug_stats['invalid_advance_ids']}"
            )
            self.logger.info(f"Final unique advances: {len(processed_df)}")

            # Log financial summary
            self.logger.info("\nFinancial Summary:")
            self.logger.info(
                f"Total Gross: ${processed_df['Sum of Syn Gross Amount'].sum():,.2f}"
            )
            self.logger.info(
                f"Total Net: ${processed_df['Sum of Syn Net Amount'].sum():,.2f}"
            )
            self.logger.info(
                f"Total Fees: ${processed_df['Total Servicing Fee'].sum():,.2f}"
            )

            # Log any processing errors
            if self.debug_stats["processing_errors"]:
                self.logger.warning("\nProcessing Errors:")
                for error in self.debug_stats["processing_errors"]:
                    self.logger.warning(f"  {error}")

            # Add additional validation checks
            # Check for expected relationships between amounts
            amount_mismatches = processed_df[
                (
                    processed_df["Sum of Syn Gross Amount"]
                    != processed_df["Sum of Syn Net Amount"]
                    + processed_df["Total Servicing Fee"]
                ).round(2)
            ]

            if not amount_mismatches.empty:
                self.logger.warning("\nAmount Relationship Mismatches Found:")
                for _, row in amount_mismatches.iterrows():
                    self.logger.warning(
                        f"  Advance ID {row['Advance ID']}: "
                        f"Gross ({row['Sum of Syn Gross Amount']}) != "
                        f"Net ({row['Sum of Syn Net Amount']}) + "
                        f"Fees ({row['Total Servicing Fee']})"
                    )

            return processed_df

        except Exception as e:
            self.logger.error(f"Error processing EFIN data: {str(e)}")
            self.debug_stats["processing_errors"].append(str(e))
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

            # Create pivot table
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
