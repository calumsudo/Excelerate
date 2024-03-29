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

def parse_kings(csv_file):
    try:
        df = pd.read_csv(csv_file)


        expected_kings_columns = [
            "Funding Date", "Advance ID", "Business Name", "Advance Status",
            "Debit Amount", "Debit Date", "Debit Cleared Date", "Debit Status",
            "Syndicators Name", "Payable Amt (Gross)", "Servicing Fee $",
            "Payable Amt (Net)", "Payable Cleared Date", "Payable Process Date",
            "Return Code"
        ]

        # Validate the columns before processing
        validate_csv_columns(df, expected_kings_columns)


        df['Payable Amt (Gross)'] = df['Payable Amt (Gross)'].replace('[\$,]', '', regex=True).astype(float)
        df['Payable Amt (Net)'] = df['Payable Amt (Net)'].replace('[\$,]', '', regex=True).astype(float)
        df['Servicing Fee $'] = df['Servicing Fee $'].replace('[\$,]', '', regex=True).astype(float)

        pivot_table = pd.pivot_table(df, values=['Payable Amt (Gross)', 'Payable Amt (Net)', 'Servicing Fee $'],
                                     index=['Business Name'],
                                     aggfunc={'Payable Amt (Gross)': 'sum',
                                              'Payable Amt (Net)': 'sum',
                                              'Servicing Fee $': 'sum'},
                                     margins=True).round(2)

        pivot_table.columns = ['Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee']
        pivot_table = pivot_table.reset_index().rename(columns={'Business Name': 'Merchant Name'})
        pivot_table = pivot_table.reindex(columns=['Merchant Name', 'Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee'])

        today_date = datetime.now().strftime("%m_%d_%Y")
        directory = os.path.expanduser("~/Desktop/Excelerator")
        os.makedirs(directory, exist_ok=True)
        output_file = f'KINGS_{today_date}.csv'
        output_path = os.path.join(directory, output_file)
        pivot_table.to_csv(output_path, index=False)

        totals_row = pivot_table[pivot_table['Merchant Name'] == 'All']
        total_gross_amount = totals_row['Sum of Syn Gross Amount'].values[0]
        total_net_amount = totals_row['Sum of Syn Net Amount'].values[0]
        total_fee = totals_row['Total Servicing Fee'].values[0]

        # No errors occurred, so return None for the error
        return pivot_table, total_gross_amount, total_net_amount, total_fee, None

    except Exception as e:
        # An error occurred, so return the error message alongside None for the other return values
        return None, None, None, None, str(e)
