import pandas as pd
from datetime import datetime
import os

def parse_bhb(csv_file):
    df = pd.read_csv(csv_file)
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

    # Include the current date in the filename for saving the CSV
    today_date = datetime.now().strftime("%m_%d_%Y")

    # Specify the directory
    directory = os.path.expanduser("~/Desktop/Excelerator")

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Create the output name
    output_file = f'BHB_{today_date}.csv'

    # Construct the full path to the output file
    output_path = os.path.join(directory, output_file)

    # Save the DataFrame to the CSV file
    pivot_table.to_csv(output_path, index=False)

    totals_row = pivot_table[pivot_table['Merchant Name'] == 'All']
    total_gross_amount = totals_row['Sum of Syn Gross Amount'].values[0]
    total_net_amount = totals_row['Sum of Syn Net Amount'].values[0]
    total_fee = totals_row['Total Servicing Fee'].values[0]

    # Return the DataFrame and totals
    return pivot_table, total_gross_amount, total_net_amount, total_fee
