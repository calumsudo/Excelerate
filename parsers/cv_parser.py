import pandas as pd

def combine_and_aggregate_reports(file_paths, output_file):
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
    
    # Calculate the total sums for 'Sum of Syn Gross Amount' and 'Sum of Syn Net Amount'
    sum_of_gross_amount = aggregated_df['Sum of Syn Gross Amount'].sum()
    sum_of_net_amount = aggregated_df['Sum of Syn Net Amount'].sum()
    
    # The formatting for dollar values is removed here, so values are no longer converted to strings with dollar signs and commas
    
    # Save the aggregated dataframe to a new CSV file
    aggregated_df.to_csv(output_file, index=False)
    
    # Return the totals
    return sum_of_gross_amount, sum_of_net_amount

# Example usage with your CSV files (replace 'monday.csv', 'tuesday.csv', etc., with actual file names)
total_gross, total_net = combine_and_aggregate_reports(
    ['dailies_cv/monday.csv', 'dailies_cv/tuesday.csv', 'dailies_cv/wednesday.csv', 'dailies_cv/thursday.csv', 'dailies_cv/friday.csv'],
    'weekly_totals_report.csv'
)

print(f"Sum of Syn Gross Amount: {total_gross:,.2f}")
print(f"Sum of Syn Net Amount: {total_net:,.2f}")
