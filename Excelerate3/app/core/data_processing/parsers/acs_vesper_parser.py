from pathlib import Path
import pandas as pd
from typing import Tuple, Optional, Dict
from .base_parser import BaseParser
from io import StringIO

class AcsVesperParser(BaseParser):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.funder_name = "VESPER"
        
    def read_csv(self) -> pd.DataFrame:
        """Override read_csv to handle VESPER's specific format"""
        try:
            # Read the CSV file into a list of lines
            with open(self.file_path, 'r') as f:
                lines = f.readlines()
            
            # Remove empty lines
            lines = [line for line in lines if line.strip()]
            
            # Find the header row index by looking for the line that starts with 'Advance ID'
            header_row_index = None
            for idx, line in enumerate(lines):
                if line.strip().startswith('Advance ID'):
                    header_row_index = idx
                    break

            if header_row_index is None:
                raise ValueError("Header row not found in the CSV file.")

            # Prepare the cleaned CSV data
            cleaned_csv = StringIO(''.join(lines))

            # Read the CSV, setting header to the identified header row
            cleaned_csv.seek(0)
            df = pd.read_csv(cleaned_csv, header=header_row_index)

            # Identify the latest 'Net' column that isn't a 'Total' column
            columns = df.columns.tolist()
            net_columns = [col for col in columns if "Net" in col and "Total" not in col]
            latest_net_column = net_columns[-1] if net_columns else None

            if latest_net_column is None:
                raise ValueError("CSV file format is incorrect or 'Net' columns are missing.")

            # Indexes for the 'Gross Payment' and 'Fees' that align with the latest 'Net' column
            latest_week_index = columns.index(latest_net_column)
            latest_gross_column = columns[latest_week_index - 2]
            latest_fees_column = columns[latest_week_index - 1]

            # Extract relevant columns for the latest week
            latest_week_df = df.iloc[:, [0, 1, latest_week_index - 2, latest_week_index - 1, latest_week_index]]

            # Find the 'Grand Total' row
            total_row = df[df["Advance ID"] == "Grand Total"]

            # Rename the columns to match expected format
            latest_week_df.columns = [
                "Advance ID",
                "Merchant Name",
                "Gross Payment",
                "Fees",
                "Net"
            ]

            # Replace NaN with 0.00 and convert to float
            latest_week_df = latest_week_df.fillna(0.00)
            
            # Convert amount columns to float
            for col in ["Gross Payment", "Fees", "Net"]:
                latest_week_df[col] = (
                    latest_week_df[col]
                    .replace(r"[\$,]", "", regex=True)
                    .astype(float)
                    .round(2)
                )
            
            # Make fees positive
            latest_week_df["Fees"] = latest_week_df["Fees"].abs()

            # Remove invalid rows
            latest_week_df = latest_week_df[
                latest_week_df["Merchant Name"].notna() &
                (latest_week_df["Merchant Name"] != 0.0) &
                (latest_week_df["Gross Payment"] != 0.0) &
                (latest_week_df["Net"] != 0.0) &
                (latest_week_df["Fees"] != 0.0)
            ]

            # Store the total row values for later use
            if not total_row.empty:
                self.total_gross = float(str(total_row[latest_gross_column].values[0]).replace("$", "").replace(",", ""))
                self.total_net = float(str(total_row[latest_net_column].values[0]).replace("$", "").replace(",", ""))
                self.total_fees = abs(float(str(total_row[latest_fees_column].values[0]).replace("$", "").replace(",", "")))
            else:
                self.total_gross = 0.0
                self.total_net = 0.0
                self.total_fees = 0.0

            self._df = latest_week_df
            return latest_week_df

        except Exception as e:
            self.logger.error(f"Error reading VESPER CSV: {str(e)}")
            raise

    def process(self) -> Tuple[pd.DataFrame, float, float, float, Optional[str]]:
        try:
            # Validate format
            is_valid, error_msg = self.validate_format()
            if not is_valid:
                return None, 0, 0, 0, error_msg

            # Create pivot table
            pivot = self.create_pivot_table(
                df=self._df,
                gross_col="Gross Payment",
                net_col="Net",
                fee_col="Fees",
                index=["Advance ID", "Merchant Name"]
            )

            # Add the totals row
            totals_row = pd.DataFrame({
                "Advance ID": ["All"],
                "Merchant Name": [""],
                "Sum of Syn Gross Amount": [self.total_gross],
                "Sum of Syn Net Amount": [self.total_net],
                "Total Servicing Fee": [self.total_fees]
            }).set_index(["Advance ID", "Merchant Name"])

            pivot = pd.concat([pivot.iloc[:-1], totals_row])

            return pivot, self.total_gross, self.total_net, self.total_fees, None

        except Exception as e:
            error_msg = f"Error processing VESPER CSV: {str(e)}"
            self.logger.error(error_msg)
            return None, 0, 0, 0, error_msg