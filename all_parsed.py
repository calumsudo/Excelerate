from parsers.kings_parser import parse_kings
from parsers.boom_parser import parse_boom
from parsers.bhb_parser import parse_bhb
from parsers.cv_parser import parse_cv
from parsers.acs_parser import parse_acs

def run_and_print(csv_file):
    # Call the parse_kings function and capture its outputs

    pivot_table, total_gross_amount, total_net_amount, total_fee = parse_acs(csv_file)
    
    # Print the pivot table
    print("Pivot Table:")
    print(pivot_table)
    
    # Print the total amounts and fee
    print(f"\nTotal Gross Amount: {total_gross_amount}")
    print(f"Total Net Amount: {total_net_amount}")
    print(f"Total Fee: {total_fee}")

# Example usage
file_paths = [
    'parsers/dailies_cv/monday.csv',
    'parsers/dailies_cv/tuesday.csv',
    'parsers/dailies_cv/wednesday.csv',
    'parsers/dailies_cv/thursday.csv',
    'parsers/dailies_cv/friday.csv'
]
run_and_print('parsers/acs_weekly.csv')