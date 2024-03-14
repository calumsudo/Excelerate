import pandas as pd
from datetime import datetime

def parse_cv(file_paths):
    # Read and combine the CSV files
    dfs = [pd.read_csv(file) for file in file_paths]
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Convert currency to numbers, remove dollar signs and commas
    combined_df['Syn Net Amount'] = combined_df['Syn Net Amount'].replace('[\$,]', '', regex=True).astype(float)
    combined_df['Syn Gross Amount'] = combined_df['Syn Gross Amount'].replace('[\$,]', '', regex=True).astype(float)
    
    # Group by 'Merchant Name' and sum up the 'Syn Net Amount' and 'Syn Gross Amount'
    aggregated_df = combined_df.groupby('Merchant Name', as_index=False).agg({
        'Syn Gross Amount': 'sum',
        'Syn Net Amount': 'sum'
    }).round(2)
    
    # Calculate the servicing fee as the difference between 'Syn Gross Amount' and 'Syn Net Amount'
    aggregated_df['Servicing Fee'] = (aggregated_df['Syn Gross Amount'] - aggregated_df['Syn Net Amount']).round(2)
    
    # Rename columns to match your requirements
    aggregated_df.columns = ['Merchant Name', 'Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee']
    
    # Calculate the total sums for 'Sum of Syn Gross Amount', 'Sum of Syn Net Amount', and 'Total Servicing Fee'
    sum_of_gross_amount = aggregated_df['Sum of Syn Gross Amount'].sum()
    sum_of_net_amount = aggregated_df['Sum of Syn Net Amount'].sum()
    sum_of_servicing_fee = aggregated_df['Total Servicing Fee'].sum()

    # Manually create and append a totals row
    totals_row = pd.DataFrame({
        'Merchant Name': ['All'],
        'Sum of Syn Gross Amount': [sum_of_gross_amount],
        'Sum of Syn Net Amount': [sum_of_net_amount],
        'Total Servicing Fee': [sum_of_servicing_fee]
    })
    aggregated_df = pd.concat([aggregated_df, totals_row], ignore_index=True)
    
    # Include the current date in the output filename
    today_date = datetime.now().strftime("%m_%d_%Y")
    output_file = f'CV_weekly_totals_report_{today_date}.csv'
    aggregated_df.to_csv(output_file, index=False)
    
    # Return the DataFrame and the totals
    return aggregated_df, sum_of_gross_amount, sum_of_net_amount, sum_of_servicing_fee
