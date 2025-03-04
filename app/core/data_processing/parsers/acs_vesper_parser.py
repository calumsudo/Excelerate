# app/core/data_processing/parsers/acs_vesper_parser.py
from pathlib import Path
import pandas as pd
from typing import Tuple, Optional
from .base_parser import BaseParser
from io import StringIO


class AcsVesperParser(BaseParser):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.funder_name = None

    def read_csv(self) -> pd.DataFrame:
        """Override read_csv to handle ACS/Vesper's specific format"""
        try:
            # Read the CSV file into a list of lines
            with open(self.file_path, "r") as f:
                self.lines = f.readlines()

            # Remove empty lines
            self.lines = [line for line in self.lines if line.strip()]

            # Find the header row index by looking for the line that starts with 'Advance ID'
            header_row_index = None
            for idx, line in enumerate(self.lines):
                if line.strip().startswith("Advance ID"):
                    header_row_index = idx
                    break

            if header_row_index is None:
                raise ValueError("Header row not found in the CSV file.")

            # Prepare the cleaned CSV data
            cleaned_csv = StringIO("".join(self.lines))

            # Read the CSV, setting header to the identified header row
            cleaned_csv.seek(0)
            df = pd.read_csv(cleaned_csv, header=header_row_index)

            # Identify the latest 'Net' column that isn't a 'Total' column
            self.columns = df.columns.tolist()
            net_columns = [
                col for col in self.columns if "Net" in col and "Total" not in col
            ]
            self.latest_net_column = net_columns[-1] if net_columns else None

            if self.latest_net_column is None:
                raise ValueError(
                    "CSV file format is incorrect or 'Net' columns are missing."
                )

            self._df = df
            return df

        except Exception as e:
            self.logger.error(f"Error reading CSV: {str(e)}")
            raise

    def get_latest_net_column(self) -> str:
        """Get the most recent net column name"""
        if not hasattr(self, "latest_net_column") or self.latest_net_column is None:
            net_columns = [
                col for col in self._df.columns if "Net" in col and "Total" not in col
            ]
            if not net_columns:
                raise ValueError("No valid Net columns found")
            self.latest_net_column = net_columns[-1]
        return self.latest_net_column

    def process_data(self) -> pd.DataFrame:
        """Process ACS/Vesper format data."""
        try:
            if self._df is None:
                raise ValueError("No data available to process")

            df = self._df.copy()

            latest_net_column = self.get_latest_net_column()
            latest_week_index = df.columns.get_loc(latest_net_column)
            latest_gross_column = df.columns[latest_week_index - 2]
            latest_fees_column = df.columns[latest_week_index - 1]

            latest_week_df = df[
                [
                    "Advance ID",
                    "Merchant Name",
                    latest_gross_column,
                    latest_fees_column,
                    latest_net_column,
                ]
            ].copy()

            # Keep any prefix (like VC or AC) in the Advance ID
            def clean_advance_id(x):
                try:
                    if pd.isna(x) or str(x).strip() == "":
                        return None
                    # Keep alphabetic prefix
                    prefix = "".join(c for c in str(x) if c.isalpha())
                    # Get numeric part
                    numeric = "".join(c for c in str(x) if c.isdigit())
                    if not numeric:
                        return None
                    return f"{prefix}{numeric}"
                except (ValueError, TypeError):
                    return None

            latest_week_df["Advance ID"] = latest_week_df["Advance ID"].apply(
                clean_advance_id
            )
            latest_week_df = latest_week_df[latest_week_df["Advance ID"].notna()]

            # Convert amounts
            for col in [latest_gross_column, latest_fees_column, latest_net_column]:
                latest_week_df[col] = (
                    pd.to_numeric(
                        latest_week_df[col]
                        .astype(str)
                        .replace(
                            {
                                r"[\$,]": "",  # Remove $ and commas
                            },
                            regex=True,
                        ),
                        errors="coerce",
                    )
                    .fillna(0)
                    .round(2)
                )

            # Filter rows with activity
            active_rows_mask = (latest_week_df[latest_gross_column] != 0) | (
                latest_week_df[latest_net_column] != 0
            )
            latest_week_df = latest_week_df[active_rows_mask]

            processed_df = pd.DataFrame(
                {
                    "Advance ID": latest_week_df["Advance ID"],
                    "Merchant Name": latest_week_df["Merchant Name"],
                    "Sum of Syn Gross Amount": latest_week_df[latest_gross_column],
                    "Total Servicing Fee": latest_week_df[latest_fees_column].abs(),
                    "Sum of Syn Net Amount": latest_week_df[latest_net_column],
                }
            )

            self.logger.info(f"Processed {len(processed_df)} rows")
            self.logger.info(
                f"Sample Advance IDs: {processed_df['Advance ID'].head().tolist()}"
            )
            self.logger.info(
                f"Total Net: {processed_df['Sum of Syn Net Amount'].sum():,.2f}"
            )

            return processed_df

        except Exception as e:
            self.logger.error(f"Error processing ACS/Vesper data: {str(e)}")
            raise

    def process(self) -> Tuple[pd.DataFrame, float, float, float, Optional[str]]:
        try:
            # Validate format
            is_valid, error_msg = self.validate_format()
            if not is_valid:
                return None, 0, 0, 0, error_msg

            # Ensure we have data loaded
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
            error_msg = (
                f"Error processing {self.funder_name or 'ACS/Vesper'} file: {str(e)}"
            )
            self.logger.error(error_msg)
            return None, 0, 0, 0, error_msg
