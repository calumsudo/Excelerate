import pandas as pd
from datetime import datetime
import os

def validate_csv_files(file_paths, required_columns):
    if len(file_paths) != 5:
        raise ValueError("There should be exactly 5 CSV files.")
    if len(file_paths) != len(set(file_paths)):
        raise ValueError("You must upload 5 unique files.")
    for file in file_paths:
        df = pd.read_csv(file)
        missing_columns = [column for column in required_columns if column not in df.columns]
        if missing_columns:
            raise ValueError(f"Incorrect file format(s) for the following {file}")

def parse_cv(file_paths, output_path, portfolio_name):
    try:
        required_columns = [
            "Last Merchant Cleared Date", "Advance Status", "AdvanceID", "Merchant Name",
            "Frequency", "Repayment Type", "Draft Amount", "Return Code", "Return Date",
            "Syn Gross Amount", "Syn Net Amount", "Syn Cleared Date", "Syndicated Amt",
            "Syndicate Purchase Price", "Syndicate Net RTR Remain"
        ]

        validate_csv_files(file_paths, required_columns)

        dfs = [pd.read_csv(file, dtype={'AdvanceID': str}) for file in file_paths]
        combined_df = pd.concat(dfs, ignore_index=True)

        currency_columns = ['Syn Net Amount', 'Syn Gross Amount']
        for column in currency_columns:
            combined_df[column] = combined_df[column].replace('[\$,]', '', regex=True).astype(float)

        # Ensure 'AdvanceID' is treated as a string
        combined_df['AdvanceID'] = combined_df['AdvanceID'].astype(str)

        # Group by 'Funder Advance ID' and 'Merchant Name'
        aggregated_df = combined_df.groupby(['AdvanceID', 'Merchant Name'], as_index=False).agg({
            'Syn Gross Amount': 'sum',
            'Syn Net Amount': 'sum'
        }).round(2)
        
        aggregated_df['Servicing Fee'] = (aggregated_df['Syn Gross Amount'] - aggregated_df['Syn Net Amount']).round(2)
        aggregated_df = aggregated_df.rename(columns={
            'AdvanceID': 'Funder Advance ID',
            'Syn Gross Amount': 'Sum of Syn Gross Amount',
            'Syn Net Amount': 'Sum of Syn Net Amount',
            'Servicing Fee': 'Total Servicing Fee'
        })

        # Calculate the totals and create a DataFrame for the totals row
        totals_data = {
            'Funder Advance ID': 'All',
            'Merchant Name': '',
            'Sum of Syn Gross Amount': aggregated_df['Sum of Syn Gross Amount'].sum(),
            'Sum of Syn Net Amount': aggregated_df['Sum of Syn Net Amount'].sum(),
            'Total Servicing Fee': aggregated_df['Total Servicing Fee'].sum()
        }
        totals_df = pd.DataFrame([totals_data])

        # Concatenate the totals DataFrame to the aggregated DataFrame
        aggregated_df = pd.concat([aggregated_df, totals_df], ignore_index=True)

        today_date = datetime.now().strftime("%m_%d_%Y")
        directory = os.path.expanduser(f"{output_path}/{portfolio_name}/{today_date}/Weekly_Pivot_Tables")
        os.makedirs(directory, exist_ok=True)
        output_file = f'ClearView_{today_date}.csv'
        output_path = os.path.join(directory, output_file)
        aggregated_df.to_csv(output_path, index=False)
        
        return aggregated_df, totals_data['Sum of Syn Gross Amount'], totals_data['Sum of Syn Net Amount'], totals_data['Total Servicing Fee'], None

    except Exception as e:
        return None, None, None, None, str(e)

