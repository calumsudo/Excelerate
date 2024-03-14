import pandas as pd
from datetime import datetime

def parse_acs(csv_file):
    # Read the CSV file, skipping the first three rows, and setting the third row as header
    df = pd.read_csv(csv_file, header=2, skiprows=[3])

    # Identify the latest 'Net' column that isn't a 'Total' column
    columns = df.columns.tolist()
    acs_columns = [col for col in columns if 'Net' in col and 'Total' not in col]
    latest_net_column = acs_columns[-1] if acs_columns else None

    if latest_net_column is None:
        print("No 'Net' column found.")
        return None, None, None, None

    # Indexes for the 'Gross Payment' and 'Fees' that align with the latest 'Net' column
    latest_week_index = columns.index(latest_net_column)
    latest_gross_column = columns[latest_week_index - 2]
    latest_fees_column = columns[latest_week_index - 1]

    # Extract relevant columns for the latest week, switching the order of 'Fees' and 'Net'
    latest_week_df = df.iloc[:, [1, latest_week_index - 2, latest_week_index, latest_week_index - 1]]
    # Rename the columns
    latest_week_df.columns = ['Merchant Name', 'Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee']

    # Replace NaN with 0.00 and convert to float
    latest_week_df.fillna(0.00, inplace=True)
    latest_week_df['Sum of Syn Gross Amount'] = latest_week_df['Sum of Syn Gross Amount'].replace('[\$,]', '', regex=True).astype(float).round(2)
    latest_week_df['Sum of Syn Net Amount'] = latest_week_df['Sum of Syn Net Amount'].replace('[\$,]', '', regex=True).astype(float).round(2)
    latest_week_df['Total Servicing Fee'] = latest_week_df['Total Servicing Fee'].replace('[\$,]', '', regex=True).astype(float).round(2)

    # Remove rows with Merchant Name as NaN, empty or 0.0
    latest_week_df = latest_week_df[(latest_week_df['Merchant Name'].notna()) & (latest_week_df['Merchant Name'] != 0.0)]

    # Find the 'Grand Total' row using the 'Advance ID' column
    total_row = df[df['Advance ID'] == 'Grand Total']

    # Get the totals from the 'Grand Total' row
    total_gross_payment = total_row[latest_gross_column].values[0] if not total_row.empty else 0.0
    total_net = total_row[latest_net_column].values[0] if not total_row.empty else 0.0
    total_fees = total_row[latest_fees_column].values[0] if not total_row.empty else 0.0

    # Manually create and append a totals row
    totals_row = pd.DataFrame({
        'Merchant Name': ['All'],
        'Sum of Syn Gross Amount': [total_gross_payment],
        'Sum of Syn Net Amount': [total_net],
        'Total Servicing Fee': [total_fees]
    })
    latest_week_df = pd.concat([latest_week_df, totals_row], ignore_index=True)
    
    # Include the current date in the filename for saving the CSV
    today_date = datetime.now().strftime("%m_%d_%Y")
    output_file = f'ACS_weekly_totals_report_{today_date}.csv'
    latest_week_df.to_csv(output_file, index=False)
    
    # Return the DataFrame and totals
    return latest_week_df, total_gross_payment, total_net, total_fees

# # Assuming 'ACS_Weekly.csv' is the path to your CSV file
# latest_week_df, total_gross_payment, total_net, total_fees = parse_acs('ACS_Weekly.csv')

# # If you want to see the dataframe or save it to a new CSV
# if latest_week_df is not None:
#     print(latest_week_df)
#     print(f"Total Sum of Syn Gross Amount: {total_gross_payment}")
#     print(f"Total Sum of Syn Net Amount: {total_net}")
#     print(f"Total Servicing Fee: {total_fees}")
