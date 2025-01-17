from pathlib import Path
import pandas as pd
import sqlite3
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass


@dataclass
class ClassificationResult:
    funder: Optional[str]
    confidence: float
    matched_ids: List[str]
    new_ids: List[str]
    reason: str


class FunderClassifier:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

        # Common ID column names across different funders
        self.possible_id_columns = ["Advance ID", "AdvanceID", "Deal ID", "DealID"]

    def _find_header_row(self, file_path: Path) -> Optional[int]:
        """Find the row containing the column headers."""
        try:
            # First read the file without header specification
            df = pd.read_csv(file_path)

            # Check if this might be a weekly format file
            if "Withdrawn per deal" in df.columns:
                # Search through rows for "Advance ID"
                for idx, row in df.iterrows():
                    if any("Advance ID" in str(val) for val in row):
                        return idx
            return None

        except Exception as e:
            self.logger.error(f"Error finding header row: {str(e)}")
            return None

    def _find_id_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the column containing advance IDs."""
        for col in self.possible_id_columns:
            if col in df.columns:
                return col
        return None

    def _get_advance_ids(self, file_path: Path) -> List[str]:
        """Extract advance IDs from the file with special handling for weekly format."""
        try:
            # Check for weekly format
            header_row = self._find_header_row(file_path)

            if header_row is not None:
                # Read file again using the correct header row
                df = pd.read_csv(file_path, skiprows=header_row)
                # Set the column names from the first row
                df.columns = df.iloc[0]
                # Remove the header row from the data
                df = df.iloc[1:]
                self.logger.info(
                    f"Found weekly format file, using header row {header_row}"
                )
            else:
                # Regular format file
                df = pd.read_csv(file_path)

            # Try to find the ID column
            id_column = self._find_id_column(df)
            if not id_column:
                self.logger.error(
                    f"Could not find ID column. Available columns: {df.columns.tolist()}"
                )
                return []

            # Clean and extract IDs
            ids = df[id_column].astype(str).str.strip()
            ids = ids[
                ids.notna() & (ids != "") & (ids != "nan") & (ids != "Grand Total")
            ]

            # Log some sample IDs for debugging
            if not ids.empty:
                self.logger.info(f"Sample IDs found: {ids.head().tolist()}")

            return ids.tolist()

        except Exception as e:
            self.logger.error(f"Error extracting advance IDs: {str(e)}")
            return []

    def _match_ids_to_funder(self, advance_ids: List[str]) -> Dict[str, List[str]]:
        """Match advance IDs to funders using the merchant_tracking database."""
        try:
            matches = {}
            with sqlite3.connect(self.db_path) as conn:
                for advance_id in advance_ids:
                    cursor = conn.execute(
                        "SELECT funder FROM merchant_tracking WHERE advance_id = ?",
                        (advance_id,),
                    )
                    result = cursor.fetchone()
                    if result:
                        funder = result[0]
                        if funder not in matches:
                            matches[funder] = []
                        matches[funder].append(advance_id)
            return matches

        except Exception as e:
            self.logger.error(f"Database error: {str(e)}")
            return {}

    def classify_funder(self, file_path: Path) -> ClassificationResult:
        """
        Classify a file by matching its advance IDs against the merchant database.
        """
        try:
            # Get advance IDs from file
            advance_ids = self._get_advance_ids(file_path)
            if not advance_ids:
                return ClassificationResult(
                    funder=None,
                    confidence=0.0,
                    matched_ids=[],
                    new_ids=[],
                    reason="No valid advance IDs found in file",
                )

            # Match IDs to funders
            funder_matches = self._match_ids_to_funder(advance_ids)

            if not funder_matches:
                return ClassificationResult(
                    funder=None,
                    confidence=0.0,
                    matched_ids=[],
                    new_ids=advance_ids,
                    reason="No matches found in merchant database",
                )

            # Find the funder with the most matches
            best_funder, matched_ids = max(
                funder_matches.items(), key=lambda x: len(x[1])
            )
            confidence = len(matched_ids) / len(advance_ids)
            new_ids = [id_ for id_ in advance_ids if id_ not in matched_ids]

            # Log the results
            self.logger.info("File classification results:")
            self.logger.info(f"Total IDs found: {len(advance_ids)}")
            self.logger.info(f"Matched to {best_funder}: {len(matched_ids)}")
            self.logger.info(f"Unmatched IDs: {len(new_ids)}")
            self.logger.info(f"Confidence: {confidence:.2%}")

            # We can be quite confident if we match even a few IDs
            # since they come from our own database
            if (
                confidence > 0.1
            ):  # Even 10% match can be confident given database source
                return ClassificationResult(
                    funder=best_funder,
                    confidence=confidence,
                    matched_ids=matched_ids,
                    new_ids=new_ids,
                    reason=f"Matched {len(matched_ids)} IDs to {best_funder}",
                )
            else:
                return ClassificationResult(
                    funder=None,
                    confidence=confidence,
                    matched_ids=matched_ids,
                    new_ids=new_ids,
                    reason=f"Insufficient matches ({confidence:.2%}) to confirm funder",
                )

        except Exception as e:
            self.logger.error(f"Error during classification: {str(e)}")
            return ClassificationResult(
                funder=None,
                confidence=0.0,
                matched_ids=[],
                new_ids=[],
                reason=f"Error during classification: {str(e)}",
            )

    def debug_classification(self, file_path: Path) -> None:
        """Enhanced debug helper to print detailed classification information."""
        try:
            print("\n=== Classification Debug ===")

            # Check for weekly format
            header_row = self._find_header_row(file_path)
            if header_row is not None:
                print(f"\nDetected weekly format file with header at row {header_row}")
                # Read file with correct header
                df = pd.read_csv(file_path, skiprows=header_row)
                df.columns = df.iloc[0]
                df = df.iloc[1:]
            else:
                print("\nRegular format file detected")
                df = pd.read_csv(file_path)

            print("\nFile columns:", df.columns.tolist())

            # Find ID column
            id_col = self._find_id_column(df)
            print(f"\nIdentified ID column: {id_col}")

            if id_col:
                print("\nSample IDs:", df[id_col].head().tolist())

            # Get all advance IDs
            advance_ids = self._get_advance_ids(file_path)
            print(f"\nTotal IDs found: {len(advance_ids)}")
            if advance_ids:
                print("Sample:", advance_ids[:5])

            # Show database matches
            funder_matches = self._match_ids_to_funder(advance_ids)
            print("\nDatabase matches:")
            for funder, ids in funder_matches.items():
                print(f"{funder}: {len(ids)} matches")

            # Run classification
            result = self.classify_funder(file_path)
            print("\nClassification Result:")
            print(f"Funder: {result.funder}")
            print(f"Confidence: {result.confidence:.2%}")
            print(f"Matched IDs: {len(result.matched_ids)}")
            print(f"New IDs: {len(result.new_ids)}")
            print(f"Reason: {result.reason}")

        except Exception as e:
            print(f"Debug error: {str(e)}")
