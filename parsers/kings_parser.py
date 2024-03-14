import pandas as pd
from datetime import datetime

def parse_kings(csv_file):
    df = pd.read_csv(csv_file)
    df['Payable Amt (Gross)'] = df['Payable Amt (Gross)'].replace('[\$,]', '', regex=True).astype(float)
    df['Payable Amt (Net)'] = df['Payable Amt (Net)'].replace('[\$,]', '', regex=True).astype(float)
    df['Servicing Fee $'] = df['Servicing Fee $'].replace('[\$,]', '', regex=True).astype(float)

    pivot_table = pd.pivot_table(df, values=['Payable Amt (Gross)', 'Payable Amt (Net)', 'Servicing Fee $'],
                                 index=['Business Name'],
                                 aggfunc={'Payable Amt (Gross)': 'sum',
                                          'Payable Amt (Net)': 'sum',
                                          'Servicing Fee $': 'sum'},
                                 margins=True).round(2)

    # Adjust column naming if needed to match the actual columns after aggregation
    pivot_table.columns = ['Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee']

    pivot_table = pivot_table.reset_index().rename(columns={'Business Name': 'Merchant Name'})
    pivot_table = pivot_table.reindex(columns=['Merchant Name', 'Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee'])

    # Format the filename with the current date
    today_date = datetime.now().strftime("%m_%d_%Y")
    filename = f'Kings_PT_{today_date}.csv'
    pivot_table.to_csv(filename, index=False)

    # Extract the totals
    totals_row = pivot_table[pivot_table['Merchant Name'] == 'All']
    total_gross_amount = totals_row['Sum of Syn Gross Amount'].values[0]
    total_net_amount = totals_row['Sum of Syn Net Amount'].values[0]
    total_fee = totals_row['Total Servicing Fee'].values[0]

    # Return the DataFrame and totals
    return pivot_table, total_gross_amount, total_net_amount, total_fee
