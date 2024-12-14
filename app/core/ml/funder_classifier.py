# app/core/ml/funder_classifier.py

from pathlib import Path
import pandas as pd
from typing import Optional, Dict, Set
from dataclasses import dataclass
import chardet
import re


@dataclass
class FunderProfile:
    name: str
    required_columns: Set[str]
    expected_column_count: int
    filename_pattern: str = None  # String to look for in filename
    unique_identifier_columns: Set[str] = None  # Columns unique to this funder
    variable_columns: bool = False  # True for ACS and Vesper
    column_patterns: Dict[str, str] = None  # Regex patterns for column matching
    identifier_weight: float = 0.6  # Weight for unique identifier columns
    min_columns: int = 0  # Minimum columns for variable formats
    max_columns: int = float('inf')  # Maximum columns for variable formats
    
class FunderClassifier:
    def __init__(self):
        # Define funder profiles with their characteristic columns and identifiers
        self.funder_profiles = {
            "ClearView": FunderProfile(
                name="ClearView",
                required_columns={
                    "Last Merchant Cleared Date",
                    "Advance Status",
                    "AdvanceID",
                    "Frequency",
                    "Repayment Type",
                    "Syn Gross Amount",
                    "Syn Net Amount"
                },
                expected_column_count=14,
                filename_pattern="syndicate_report",
                unique_identifier_columns={"Syndicate Net RTR Remain"}
            ),
            
            "BHB": FunderProfile(
                name="BHB",
                required_columns={
                    "Deal ID",
                    "Deal Name",
                    "Participator Gross Amount",
                    "Fee",
                    "Net Payment Amount"
                },
                expected_column_count=9,
                unique_identifier_columns={"Balance", "Res. Commission"}
            ),
            
            "EFIN": FunderProfile(
                name="EFIN",
                required_columns={
                    "Funding Date",
                    "Advance ID",
                    "Business Name",
                    "Advance Status",
                    "Payable Amt (Gross)",
                    "Servicing Fee $",
                    "Payable Amt (Net)"
                },
                expected_column_count=19,
                unique_identifier_columns={"Freq", "Repay Type"}
            ),
            
            "Kings": FunderProfile(
                name="Kings",
                required_columns={
                    "Funding Date",
                    "Advance ID",
                    "Business Name",
                    "Payable Amt (Gross)",
                    "Servicing Fee $",
                    "Payable Amt (Net)"
                },
                expected_column_count=14,
                unique_identifier_columns={"Payable Process Date"}
            ),

            "Boom": FunderProfile(
                name="Boom",
                required_columns={
                    "Funding Date",
                    "Advance ID",
                    "Business Name",
                    "Payable Amt (Gross)",
                    "Servicing Fee $",
                    "Payable Amt (Net)"
                },
                expected_column_count=14,
                unique_identifier_columns={"Payable Status"}
            ),

            
            "Vesper": FunderProfile(
                name="Vesper",
                required_columns={
                    "Advance ID",
                    "Merchant Name",
                    "Gross Payment",
                    "Fees",
                    "Net"
                },
                expected_column_count=0,  # Variable
                filename_pattern="VESPER CAPITAL",
                variable_columns=True,
                column_patterns={
                    'base_columns': r'^(Advance ID|Merchant Name)$',
                    'week_columns': r'^Week\s*,+$',
                    'date_columns': r'\d{1,2}/\d{1,2}/\d{4}'
                }
            ),
            
            "ACS": FunderProfile(
                name="ACS",
                required_columns={
                    "Advance ID",
                    "Merchant Name",
                    "Gross Payment",
                    "Fees",
                    "Net"
                },
                expected_column_count=0,  # Variable
                filename_pattern="ACS",
                variable_columns=True,
                column_patterns={
                    'base_columns': r'^(Advance ID|Merchant Name)$',
                    'week_columns': r'^Week\s*,+$',
                    'date_columns': r'\d{1,2}/\d{1,2}/\d{4}'
                }
            ),
        }

    def detect_encoding(self, file_path: Path) -> str:
        """Detect the file encoding."""
        with open(file_path, 'rb') as file:
            raw_data = file.read(10000)
            result = chardet.detect(raw_data)
            return result['encoding']
        
    def analyze_column_patterns(self, columns: Set[str], profile: FunderProfile) -> Dict:
        """Analyze columns for pattern matches."""
        if not profile.column_patterns:
            return {}
            
        results = {'pattern_matches': 0, 'total_patterns': len(profile.column_patterns)}
        
        for col in columns:
            for pattern_name, pattern in profile.column_patterns.items():
                if re.search(pattern, col):
                    results[f'{pattern_name}_found'] = True
                    results['pattern_matches'] += 1
                    break
        
        return results

    def get_file_info(self, file_path: Path) -> Optional[Dict]:
        """Extract file information including columns and count."""
        try:
            encodings_to_try = [
                self.detect_encoding(file_path),
                'utf-8',
                'cp1252',
                'iso-8859-1'
            ]
            
            for encoding in encodings_to_try:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    return {
                        'columns': set(df.columns),
                        'column_count': len(df.columns),
                        'filename': file_path.name.lower()
                    }
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Error reading file with {encoding}: {str(e)}")
                    continue
            
            return None
        except Exception as e:
            print(f"Error getting file info: {str(e)}")
            return None

    def calculate_match_score(self, file_info: Dict, profile: FunderProfile) -> Dict:
        """Calculate how well the file matches a funder profile with detailed scoring."""
        scores = {
            'total': 0.0,
            'components': {}
        }
        
        # For non-variable funders, check column count
        if not profile.variable_columns:
            column_match = file_info['column_count'] == profile.expected_column_count
            scores['components']['column_count'] = {
                'score': 1.0 if column_match else 0.0,
                'weight': 0.4,
                'details': f"{'Matches' if column_match else 'Does not match'} expected {profile.expected_column_count} columns"
            }
            
            # If column count matches, check unique identifier columns
            if column_match and profile.unique_identifier_columns:
                unique_matches = sum(1 for col in profile.unique_identifier_columns if col in file_info['columns'])
                unique_score = unique_matches / len(profile.unique_identifier_columns)
                scores['components']['unique_columns'] = {
                    'score': unique_score,
                    'weight': 0.6,
                    'details': f"Found {unique_matches} of {len(profile.unique_identifier_columns)} unique columns"
                }
            
            # If column count doesn't match, assign very low total score
            if not column_match:
                scores['total'] = 0.0
                return scores
        
        # For variable column funders
        else:
            if file_info['column_count'] > 20:
                scores['components']['column_count'] = {
                    'score': 1.0,
                    'weight': 0.4,
                    'details': f"Large column count ({file_info['column_count']}) matches variable format"
                }
            else:
                scores['components']['column_count'] = {
                    'score': 0.0,
                    'weight': 0.4,
                    'details': f"Column count too low ({file_info['column_count']}) for variable format"
                }

        # Filename pattern
        if profile.filename_pattern:
            filename_score = 1.0 if profile.filename_pattern.lower() in file_info['filename'].lower() else 0.0
            scores['components']['filename'] = {
                'score': filename_score,
                'weight': 0.2,
                'details': f"Pattern '{profile.filename_pattern}' {'found' if filename_score > 0 else 'not found'}"
            }

        # Column patterns for variable column funders
        if profile.variable_columns and profile.column_patterns:
            pattern_results = self.analyze_column_patterns(file_info['columns'], profile)
            pattern_score = pattern_results['pattern_matches'] / pattern_results['total_patterns']
            scores['components']['patterns'] = {
                'score': pattern_score,
                'weight': 0.4,
                'details': f"Found {pattern_results['pattern_matches']} of {pattern_results['total_patterns']} expected patterns"
            }

        # Calculate total score
        total_weight = sum(comp['weight'] for comp in scores['components'].values())
        if total_weight > 0:
            scores['total'] = sum(comp['score'] * comp['weight'] 
                                for comp in scores['components'].values()) / total_weight

        return scores
    
    def classify_funder(self, file_path: Path) -> Optional[Dict[str, Dict]]:
        """Classify a CSV file by funder with detailed scoring."""
        try:
            file_info = self.get_file_info(file_path)
            if not file_info:
                return None
                
            results = {}
            for funder_name, profile in self.funder_profiles.items():
                scores = self.calculate_match_score(file_info, profile)
                results[funder_name] = scores
            
            # Sort by total score
            return dict(sorted(results.items(), key=lambda x: x[1]['total'], reverse=True))
            
        except Exception as e:
            print(f"Error classifying file: {str(e)}")
            return None
            

    def get_best_match(self, file_path: Path, threshold: float = 0.6) -> Optional[str]:
        """
        Get the best matching funder name if its score exceeds the threshold.
        Returns None if no funder matches well enough.
        
        Args:
            file_path: Path to the file to classify
            threshold: Default threshold for matching (0.6 works better than 0.7)
            
        Returns:
            Optional[str]: Name of best matching funder or None if no match found
        """
        scores = self.classify_funder(file_path)
        if not scores:
            return None
            
        # Get funder with highest total score
        best_funder = max(scores.items(), key=lambda x: x[1]['total'])
        funder_name, score_data = best_funder
        
        # Use lower threshold for variable column funders (ACS and Vesper)
        if funder_name in ["ACS", "Vesper"]:
            variable_threshold = 0.5  # Lower threshold for ACS/Vesper
            return funder_name if score_data['total'] >= variable_threshold else None
        
        return funder_name if score_data['total'] >= threshold else None

    def explain_classification(self, file_path: Path) -> None:
        """
        Provide detailed explanation of the classification process and results.
        """
        try:
            file_info = self.get_file_info(file_path)
            if not file_info:
                print("Could not read file information")
                return
                
            print(f"\nFile Analysis for: {file_path.name}")
            print(f"Number of columns: {file_info['column_count']}")
            
            scores = self.classify_funder(file_path)
            if not scores:
                print("Could not calculate scores")
                return
                
            print("\nMatching scores and reasons:")
            for funder, score_data in scores.items():
                profile = self.funder_profiles[funder]
                print(f"\n{funder}: {score_data['total']:.3f}")
                
                # Print score components
                for component, details in score_data['components'].items():
                    print(f"- {component}: {details['score']:.3f} (weight: {details['weight']:.2f})")
                    print(f"  {details['details']}")
                
            # Print best match
            best_match = max(scores.items(), key=lambda x: x[1]['total'])
            print(f"\nBest match: {best_match[0]} (score: {best_match[1]['total']:.3f})")
                
        except Exception as e:
            print(f"Error explaining classification: {str(e)}")