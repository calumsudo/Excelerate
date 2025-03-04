# app/core/data_processing/parsers/base_parser.py

from abc import ABC, abstractmethod
import pandas as pd
from typing import Tuple, Optional, Dict
from pathlib import Path
import chardet
import logging


class BaseParser(ABC):
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.required_columns: list = []
        self.column_types: Dict[str, type] = {}
        self.funder_name: str = ""
        self._df: Optional[pd.DataFrame] = None

        # Setup logging
        self.logger = logging.getLogger(f"parser.{self.__class__.__name__}")

    def detect_encoding(self) -> str:
        with open(self.file_path, "rb") as file:
            raw_data = file.read(10000)
            result = chardet.detect(raw_data)
            return result["encoding"]

    def read_csv(self) -> pd.DataFrame:
        encodings_to_try = [self.detect_encoding(), "utf-8", "cp1252", "iso-8859-1"]

        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(self.file_path, encoding=encoding)
                self._df = df
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.error(f"Error reading CSV with {encoding}: {str(e)}")
                continue

        raise ValueError(f"Unable to read {self.file_path} with any encoding")

    def validate_format(self) -> Tuple[bool, str]:
        if self._df is None:
            self._df = self.read_csv()

        missing_columns = [
            col for col in self.required_columns if col not in self._df.columns
        ]
        if missing_columns:
            return False, f"Missing columns: {', '.join(missing_columns)}"

        for column, expected_type in self.column_types.items():
            try:
                if expected_type is float:
                    self._df[column] = (
                        self._df[column]
                        .replace({r"[\$,]": "", r"\(": "-", r"\)": ""}, regex=True)
                        .astype(float)
                    )
                else:
                    self._df[column] = self._df[column].astype(expected_type)
            except Exception as e:
                return False, f"Error converting {column} to {expected_type}: {str(e)}"

        return True, ""

    @abstractmethod
    def process(self) -> Tuple[pd.DataFrame, float, float, float, Optional[str]]:
        pass

    def create_pivot_table(
        self,
        df: pd.DataFrame,
        gross_col: str,
        net_col: str,
        fee_col: str,
        index: list,
        aggfunc: str = "sum",
    ) -> pd.DataFrame:
        """
        Create a standardized pivot table with consistent formatting.

        Args:
            df: Source DataFrame with columns:
                - "Advance ID"
                - "Merchant Name" (or equivalent)
                - gross_col: column for gross amounts
                - net_col: column for net amounts
                - fee_col: column for fees
        """
        try:
            # First standardize the input column names
            df = df.copy()

            # Standardize the merchant/business name column to "Merchant Name"
            name_columns = [
                "Business Name",
                "Merchant Name",
                "business_name",
                "merchant_name",
            ]
            for col in name_columns:
                if col in df.columns:
                    df["Merchant Name"] = df[col]
                    break

            # Create pivot table
            pivot = pd.pivot_table(
                df,
                values=[gross_col, net_col, fee_col],
                index=index,
                aggfunc=aggfunc,
                margins=True,
                margins_name="Totals",  # This sets 'Totals' instead of 'All'
            ).round(2)

            # Reset index to make index columns regular columns
            pivot = pivot.reset_index()

            # Rename columns to standard names and reorder
            pivot.columns = [
                col
                if col in ["Advance ID", "Merchant Name"]
                else {
                    gross_col: "Sum of Syn Gross Amount",
                    net_col: "Sum of Syn Net Amount",
                    fee_col: "Total Servicing Fee",
                }[col]
                for col in pivot.columns
            ]

            # Set empty string in Merchant Name column for totals row
            totals_mask = pivot["Advance ID"] == "Totals"
            pivot.loc[totals_mask, "Merchant Name"] = ""

            # Reorder columns to standard order
            standard_columns = [
                "Advance ID",
                "Merchant Name",
                "Sum of Syn Gross Amount",
                "Total Servicing Fee",
                "Sum of Syn Net Amount",
            ]

            pivot = pivot[standard_columns]

            return pivot

        except Exception as e:
            self.logger.error(f"Error creating pivot table: {str(e)}")
            raise
