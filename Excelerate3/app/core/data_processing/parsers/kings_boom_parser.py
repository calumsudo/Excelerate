from pathlib import Path
import pandas as pd
from typing import Tuple, Optional, Dict
from .base_parser import BaseParser

class KingsBoomParser(BaseParser):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.funder_name = "Kings"
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

    def process(self) -> Tuple[pd.DataFrame, float, float, float, Optional[str]]:
        try:
            # Validate format
            is_valid, error_msg = self.validate_format()
            if not is_valid:
                return None, 0, 0, 0, error_msg

            # Create pivot table
            pivot = self.create_pivot_table(
                df=self._df,
                gross_col="Payable Amt (Gross)",
                net_col="Payable Amt (Net)",
                fee_col="Servicing Fee $",
                index=["Advance ID", "Business Name"]
            )

            # Get totals from the last row
            totals = pivot.iloc[-1]
            total_gross = totals["Sum of Syn Gross Amount"]
            total_net = totals["Sum of Syn Net Amount"]
            total_fee = totals["Total Servicing Fee"]

            return pivot, total_gross, total_net, total_fee, None

        except Exception as e:
            error_msg = f"Error processing Kings CSV: {str(e)}"
            self.logger.error(error_msg)
            return None, 0, 0, 0, error_msg
