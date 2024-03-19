from parsers.kings_parser import parse_kings
from parsers.boom_parser import parse_boom
from parsers.bhb_parser import parse_bhb
from parsers.cv_parser import parse_cv
from parsers.acs_parser import parse_acs

def run_and_print(kings_csv_file, boom_csv_file, bhb_csv_file, acs_csv_file, cv_csv_files):
    # Call the all parsing functions and capture its outputs
    kings_pivot_table, kings_total_gross_amount, kings_total_net_amount, kings_total_fee = parse_kings(kings_csv_file)
    boom_pivot_table, boom_total_gross_amount, boom_total_net_amount, boom_total_fee = parse_boom(boom_csv_file)
    bhb_pivot_table, bhb_total_gross_amount, bhb_total_net_amount, bhb_total_fee = parse_bhb(bhb_csv_file)
    cv_pivot_table, cv_total_gross_amount, cv_total_net_amount, cv_total_fee = parse_cv(cv_csv_files)
    acs_pivot_table, acs_total_gross_amount, acs_total_net_amount, acs_total_fee = parse_acs(acs_csv_file)

    print("Kings")
    print(kings_pivot_table)
    print(f"\nTotal Gross Amount: {kings_total_gross_amount}")
    print(f"Total Net Amount: {kings_total_net_amount}")
    print(f"Total Fee: {kings_total_fee}")

    print("\nBoom")
    print(boom_pivot_table)
    print(f"\nTotal Gross Amount: {boom_total_gross_amount}")
    print(f"Total Net Amount: {boom_total_net_amount}")
    print(f"Total Fee: {boom_total_fee}")

    print("\nBHB")
    print(bhb_pivot_table)
    print(f"\nTotal Gross Amount: {bhb_total_gross_amount}")
    print(f"Total Net Amount: {bhb_total_net_amount}")
    print(f"Total Fee: {bhb_total_fee}")

    print("\nCV")
    print(cv_pivot_table)
    print(f"\nTotal Gross Amount: {cv_total_gross_amount}")
    print(f"Total Net Amount: {cv_total_net_amount}")
    print(f"Total Fee: {cv_total_fee}")

    print("\nACS")
    print(acs_pivot_table)
    print(f"\nTotal Gross Amount: {acs_total_gross_amount}")
    print(f"Total Net Amount: {acs_total_net_amount}")
    print(f"Total Fee: {acs_total_fee}")

    return {
        "kings_pivot_table": kings_pivot_table,
        "kings_total_gross_amount": kings_total_gross_amount,
        "kings_total_net_amount": kings_total_net_amount,
        "kings_total_fee": kings_total_fee,
        "boom_pivot_table": boom_pivot_table,
        "boom_total_gross_amount": boom_total_gross_amount,
        "boom_total_net_amount": boom_total_net_amount,
        "boom_total_fee": boom_total_fee,
        "bhb_pivot_table": bhb_pivot_table,
        "bhb_total_gross_amount": bhb_total_gross_amount,
        "bhb_total_net_amount": bhb_total_net_amount,
        "bhb_total_fee": bhb_total_fee,
        "cv_pivot_table": cv_pivot_table,
        "cv_total_gross_amount": cv_total_gross_amount,
        "cv_total_net_amount": cv_total_net_amount,
        "cv_total_fee": cv_total_fee,
        "acs_pivot_table": acs_pivot_table,
        "acs_total_gross_amount": acs_total_gross_amount,
        "acs_total_net_amount": acs_total_net_amount,
        "acs_total_fee": acs_total_fee
    }

    

    

# Example usage
# kings_csv_file = 'csv/kings.csv'
# boom_csv_file = 'csv/boom.csv'
# bhb_csv_file = 'csv/bhb.csv'
# acs_csv_file = 'csv/acs.csv'
# cv_csv_files = [
#     'csv/dailies_cv/monday.csv',
#     'csv/dailies_cv/tuesday.csv',
#     'csv/dailies_cv/wednesday.csv',
#     'csv/dailies_cv/thursday.csv',
#     'csv/dailies_cv/friday.csv'
# ]

# run_and_print(kings_csv_file, boom_csv_file, bhb_csv_file, acs_csv_file, cv_csv_files)