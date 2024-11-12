# core/data_processing/parsers/base_parser.py
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
        with open(self.file_path, 'rb') as file:
            raw_data = file.read(10000)
            result = chardet.detect(raw_data)
            return result['encoding']

    def read_csv(self) -> pd.DataFrame:
        encodings_to_try = [
            self.detect_encoding(),
            'utf-8',
            'cp1252',
            'iso-8859-1'
        ]
        
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
            
        missing_columns = [col for col in self.required_columns 
                         if col not in self._df.columns]
        if missing_columns:
            return False, f"Missing columns: {', '.join(missing_columns)}"
            
        for column, expected_type in self.column_types.items():
            try:
                if expected_type == float:
                    self._df[column] = self._df[column].replace({
                        r'[\$,]': '',
                        r'\(': '-',
                        r'\)': ''
                    }, regex=True).astype(float)
                else:
                    self._df[column] = self._df[column].astype(expected_type)
            except Exception as e:
                return False, f"Error converting {column} to {expected_type}: {str(e)}"
                
        return True, ""

    @abstractmethod
    def process(self) -> Tuple[pd.DataFrame, float, float, float, Optional[str]]:
        pass

    def create_pivot_table(self, 
                        df: pd.DataFrame,
                        gross_col: str,
                        net_col: str,
                        fee_col: str,
                        index: list,
                        aggfunc: str = "sum") -> pd.DataFrame:
        """
        Create a standardized pivot table with index columns included.
        
        Args:
            df: Source DataFrame
            gross_col: Name of gross amount column
            net_col: Name of net amount column
            fee_col: Name of fee column
            index: Columns to group by
            aggfunc: Aggregation function
        """
        # Create pivot table
        pivot = pd.pivot_table(
            df,
            values=[gross_col, net_col, fee_col],
            index=index,
            aggfunc=aggfunc,
            margins=True
        ).round(2)
        
        # Rename columns to standard names
        column_mapping = {
            gross_col: 'Sum of Syn Gross Amount',
            net_col: 'Sum of Syn Net Amount',
            fee_col: 'Total Servicing Fee'
        }
        pivot.columns = [column_mapping.get(col, col) for col in pivot.columns]
        
        # Reset the index to make the index columns regular columns
        pivot = pivot.reset_index()
        
        # Handle the 'All' row in the index columns
        # Replace 'All' with empty string in all but the first index column
        total_row_mask = pivot[index[0]] == 'All'
        for col in index[1:]:
            pivot.loc[total_row_mask, col] = ''
            
        return pivot
