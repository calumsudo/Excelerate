import pandas as pd
from datetime import datetime
import os

def validate_csv_files(file_paths, required_columns):
    # Check for the number of files
    if len(file_paths) != 5:
        raise ValueError("There should be exactly 5 CSV files.")
    
    # Check for duplicate files
    if len(file_paths) != len(set(file_paths)):
        raise ValueError("Duplicate files detected.")

    # Validate the columns for each file
    for file in file_paths:
        df = pd.read_csv(file)
        missing_columns = [column for column in required_columns if column not in df.columns]
        if missing_columns:
            raise ValueError(f"Incorrect file format(s) for the following{file}")


def parse_cv(file_paths, output_path):
    try:
        # Expected columns
        required_columns = [
            "Last Merchant Cleared Date", "Advance Status", "AdvanceID", "Merchant Name",
            "Frequency", "Repayment Type", "Draft Amount", "Return Code", "Return Date",
            "Syn Gross Amount", "Syn Net Amount", "Syn Cleared Date", "Syndicated Amt",
            "Syndicate Purchase Price", "Syndicate Net RTR Remain"
        ]

        # Validate files
        validate_csv_files(file_paths, required_columns)

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
        

        # Include the current date in the filename for saving the CSV
        today_date = datetime.now().strftime("%m_%d_%Y")

        # Specify the directory
        directory = os.path.expanduser(f"{output_path}/{today_date}/Weekly_Pivot_Tables")

        # Create the directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Create the output name
        output_file = f'ClearView_{today_date}.csv'

        # Construct the full path to the output file
        output_path = os.path.join(directory, output_file)

        # Save the DataFrame to the CSV file
        aggregated_df.to_csv(output_path, index=False)
        
        # Return the DataFrame and the totals
        return aggregated_df, sum_of_gross_amount, sum_of_net_amount, sum_of_servicing_fee, None

    except Exception as e:
        return None, None, None, None, str(e)