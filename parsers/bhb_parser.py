
import pandas as pd
from datetime import datetime
import os

def validate_csv_columns(df, required_columns):
    # Check if all required columns are in the DataFrame
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        # Limit the display to the first 5 missing columns
        limited_missing_columns = missing_columns[:3]
        message = f"the following columns: {', '.join(limited_missing_columns)}"
        if len(missing_columns) > 5:
            message += ", ..."
        raise ValueError(message)

def parse_bhb(csv_file, output_path):
    try:
        df = pd.read_csv(csv_file)

        # Define the expected columns for the BHB CSV
        expected_bhb_columns = [
            "Deal ID", "Deal Name", "Participator Gross Amount", "Non Qualifying Collections",
            "Total Reversals", "Fee", "Res. Commission", "Net Payment Amount", "Balance"
        ]

        # Validate the columns before processing
        validate_csv_columns(df, expected_bhb_columns)

        # Proceed with processing if validation passes
        df['Participator Gross Amount'] = df['Participator Gross Amount'].replace('[\$,]', '', regex=True).astype(float)
        df['Net Payment Amount'] = df['Net Payment Amount'].replace('[\$,]', '', regex=True).astype(float)
        df['Fee'] = df['Fee'].replace('[\$,]', '', regex=True).astype(float)

        pivot_table = pd.pivot_table(df, values=['Participator Gross Amount', 'Net Payment Amount', 'Fee'],
                                     index=['Deal Name'],
                                     aggfunc={'Participator Gross Amount': 'sum',
                                              'Net Payment Amount': 'sum',
                                              'Fee': 'sum'},
                                     margins=True).round(2)

        pivot_table.columns = ['Total Servicing Fee', 'Sum of Syn Net Amount', 'Sum of Syn Gross Amount']
        pivot_table = pivot_table.reset_index().rename(columns={'Deal Name': 'Merchant Name'})
        pivot_table = pivot_table.reindex(columns=['Merchant Name', 'Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee'])

        today_date = datetime.now().strftime("%m_%d_%Y")
        directory = os.path.expanduser(f"{output_path}/{today_date}/Weekly_Pivot_Tables")
        os.makedirs(directory, exist_ok=True)
        output_file = f'BHB_{today_date}.csv'
        output_path = os.path.join(directory, output_file)
        pivot_table.to_csv(output_path, index=False)

        totals_row = pivot_table[pivot_table['Merchant Name'] == 'All']
        total_gross_amount = totals_row['Sum of Syn Gross Amount'].values[0]
        total_net_amount = totals_row['Sum of Syn Net Amount'].values[0]
        total_fee = totals_row['Total Servicing Fee'].values[0]

        return pivot_table, total_gross_amount, total_net_amount, total_fee, None

    except Exception as e:
        # An error occurred, so return the error message alongside None for the other return values
        return None, None, None, None, str(e)
