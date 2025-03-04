# app/core/data_processing/parsers/clear_view_parser.py

from pathlib import Path
import pandas as pd
from typing import Tuple, Optional, List, Union
from .base_parser import BaseParser


class ClearViewParser(BaseParser):
    def __init__(self, file_path: Union[Path, List[Path]]):
        """
        Initialize the ClearView parser with one or more file paths.

        Args:
            file_path: Either a single Path or a list of Paths to ClearView reports
        """
        # Store all file paths
        self.all_file_paths = (
            [Path(file_path)]
            if isinstance(file_path, (str, Path))
            else [Path(p) for p in file_path]
        )

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
            "Syndicate Net RTR Remain",
        ]
        self.column_types = {
            "AdvanceID": str,
            "Syn Gross Amount": float,
            "Syn Net Amount": float,
        }

        self._combined_df = None

        # Log initialization
        self.logger.info(
            f"Initializing ClearView parser with {len(self.all_file_paths)} files"
        )
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
        """Process ClearView files with logging"""
        try:
            all_data = []
            for file_path in self.all_file_paths:
                df = pd.read_csv(file_path)
                self.logger.info(f"Reading file {file_path.name}")
                self.logger.info(
                    f"Sample AdvanceIDs: {df['AdvanceID'].head().tolist()}"
                )
                self.logger.info(
                    f"Sample amounts: {df['Syn Net Amount'].head().tolist()}"
                )
                all_data.append(df)
            combined = pd.concat(all_data, ignore_index=True)
            self._df = combined
            return combined
        except Exception as e:
            self.logger.error(f"Error reading CSV: {str(e)}")
            raise

    def validate_format(self) -> Tuple[bool, str]:
        """Validate format of all provided files."""
        try:
            for file_path in self.all_file_paths:
                encodings_to_try = [
                    self.detect_encoding(),
                    "utf-8",
                    "cp1252",
                    "iso-8859-1",
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
                missing_columns = [
                    col for col in self.required_columns if col not in df.columns
                ]
                if missing_columns:
                    return (
                        False,
                        f"Missing columns in {file_path.name}: {', '.join(missing_columns)}",
                    )

            return True, ""

        except Exception as e:
            return False, str(e)

    def process_data(self) -> pd.DataFrame:
        try:
            # Make a copy of the DataFrame to avoid SettingWithCopyWarning
            combined = self._df.copy()

            # Clean IDs
            combined["AdvanceID"] = pd.to_numeric(
                combined["AdvanceID"], errors="coerce"
            )
            combined.dropna(subset=["AdvanceID"], inplace=True)
            combined["AdvanceID"] = combined["AdvanceID"].astype(int).astype(str)

            # Convert amounts and handle zeros
            for col in ["Syn Gross Amount", "Syn Net Amount"]:
                combined[col] = pd.to_numeric(
                    combined[col]
                    .astype(str)
                    .replace("[,$()]", "", regex=True)
                    .replace("", "0"),
                    errors="coerce",
                ).fillna(0.0)
                combined[col] = combined[col].round(2)

            # Exclude rows where both amounts are zero
            combined = combined[
                (combined["Syn Gross Amount"] != 0.0)
                | (combined["Syn Net Amount"] != 0.0)
            ]

            # Group and sum
            grouped = combined.groupby("AdvanceID", as_index=False).agg(
                {"Syn Gross Amount": "sum", "Syn Net Amount": "sum"}
            )

            # Calculate Total Servicing Fee with decimals
            grouped["Total Servicing Fee"] = (
                (grouped["Syn Gross Amount"] - grouped["Syn Net Amount"]).abs().round(2)
            )

            processed_df = pd.DataFrame(
                {
                    "Advance ID": grouped["AdvanceID"],
                    "Merchant Name": grouped[
                        "AdvanceID"
                    ],  # Replace with actual merchant names if available
                    "Sum of Syn Gross Amount": grouped["Syn Gross Amount"],
                    "Sum of Syn Net Amount": grouped["Syn Net Amount"],
                    "Total Servicing Fee": grouped["Total Servicing Fee"],
                }
            )

            return processed_df

        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
            raise

    def process(self) -> Tuple[pd.DataFrame, float, float, float, Optional[str]]:
        try:
            # First validate format
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

            # Calculate totals directly from processed DataFrame
            total_gross = processed_df["Sum of Syn Gross Amount"].sum()
            total_net = processed_df["Sum of Syn Net Amount"].sum()
            total_fee = processed_df["Total Servicing Fee"].sum()

            # Create pivot table using base parser method
            pivot = self.create_pivot_table(
                df=processed_df,
                gross_col="Sum of Syn Gross Amount",
                net_col="Sum of Syn Net Amount",
                fee_col="Total Servicing Fee",
                index=["Advance ID", "Merchant Name"],
            )

            return pivot, total_gross, total_net, total_fee, None

        except Exception as e:
            error_msg = f"Error processing ClearView file: {str(e)}"
            self.logger.error(error_msg)
            return None, 0, 0, 0, error_msg
