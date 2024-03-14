import pandas as pd
from datetime import datetime

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

    # Include the current date in the filename
    today_date = datetime.now().strftime("%m_%d_%Y")
    filename = f'BHB_PT_{today_date}.csv'
    pivot_table.to_csv(filename, index=False)

    totals_row = pivot_table[pivot_table['Merchant Name'] == 'All']
    total_gross_amount = totals_row['Sum of Syn Gross Amount'].values[0]
    total_net_amount = totals_row['Sum of Syn Net Amount'].values[0]
    total_fee = totals_row['Total Servicing Fee'].values[0]

    # Return the DataFrame and totals
    return pivot_table, total_gross_amount, total_net_amount, total_fee
