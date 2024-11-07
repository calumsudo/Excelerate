from abc import ABC, abstractmethod
import pandas as pd
from typing import Tuple, Optional
from pathlib import Path

class BaseParser(ABC):
    """Abstract base class for all funder parsers."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.required_columns = []
        self.funder_name = ""

    @abstractmethod
    def validate_format(self) -> Tuple[bool, str]:
        """Validate the CSV format."""
        pass

    @abstractmethod
    def process(self) -> Tuple[pd.DataFrame, float, float, float, Optional[str]]:
        """Process the CSV and return pivot table data."""
        pass

    def _validate_columns(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """Common column validation logic."""
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            return False, f"Missing columns: {', '.join(missing_columns)}"
        return True, ""
