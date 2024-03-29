# import pandas as pd
# from datetime import datetime
# import os

# def parse_boom(csv_file):
#     df = pd.read_csv(csv_file)
#     df['Payable Amt (Gross)'] = df['Payable Amt (Gross)'].replace('[\$,]', '', regex=True).astype(float)
#     df['Payable Amt (Net)'] = df['Payable Amt (Net)'].replace('[\$,]', '', regex=True).astype(float)
#     df['Servicing Fee $'] = df['Servicing Fee $'].replace('[\$,]', '', regex=True).astype(float)

#     pivot_table = pd.pivot_table(df, values=['Payable Amt (Gross)', 'Payable Amt (Net)', 'Servicing Fee $'],
#                                  index=['Business Name'],
#                                  aggfunc={'Payable Amt (Gross)': 'sum',
#                                           'Payable Amt (Net)': 'sum',
#                                           'Servicing Fee $': 'sum'},
#                                  margins=True).round(2)

#     pivot_table.columns = ['Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee']
#     pivot_table = pivot_table.reset_index().rename(columns={'Business Name': 'Merchant Name'})
#     pivot_table = pivot_table.reindex(columns=['Merchant Name', 'Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee'])


#     # Include the current date in the filename for saving the CSV
#     today_date = datetime.now().strftime("%m_%d_%Y")

#     # Specify the directory
#     directory = os.path.expanduser("~/Desktop/Excelerator")

#     # Create the directory if it doesn't exist
#     os.makedirs(directory, exist_ok=True)

#     # Create the output name
#     output_file = f'BOOM_{today_date}.csv'

#     # Construct the full path to the output file
#     output_path = os.path.join(directory, output_file)

#     # Save the DataFrame to the CSV file
#     pivot_table.to_csv(output_path, index=False)

#     totals_row = pivot_table[pivot_table['Merchant Name'] == 'All']
#     total_gross_amount = totals_row['Sum of Syn Gross Amount'].values[0]
#     total_net_amount = totals_row['Sum of Syn Net Amount'].values[0]
#     total_fee = totals_row['Total Servicing Fee'].values[0]

#     # Return the DataFrame and totals
#     return pivot_table, total_gross_amount, total_net_amount, total_fee


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

def parse_boom(csv_file):
    try:
        df = pd.read_csv(csv_file)

        # Define the expected columns for the Boom CSV
        expected_boom_columns = [
            "Business Name", "Payable Amt (Gross)", "Servicing Fee $", "Payable Amt (Net)",
            "Syndicators Name", "Payable Cleared Date", "Payable Status", "Advance ID",
            "Funding Date", "Sub-Type", "Debit Amount", "Debit Cleared Date",
            "Debit Date", "Debit Status"
        ]

        # Validate the columns before processing
        validate_csv_columns(df, expected_boom_columns)

        # Proceed with processing if validation passes
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
        output_file = f'BOOM_{today_date}.csv'
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
