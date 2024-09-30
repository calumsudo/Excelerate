# import pandas as pd
# from datetime import datetime
# import os

# def currency_to_float(value):
#     """
#     Converts a currency string to a float. Handles negative values indicated by parentheses.
#     """
#     if isinstance(value, str):
#         value = (
#             value.replace("$", "")
#             .replace(",", "")
#             .replace("(", "-")
#             .replace(")", "")
#             .strip()
#         )
#     try:
#         return float(value)
#     except ValueError:
#         return 0.0  # Handle cases where the value is not a number

# def parse_vesper(csv_file, output_path, portfolio_name):
#     try:
#         # Read the CSV file without headers
#         df = pd.read_csv(csv_file, header=None)

#         # Remove completely empty rows
#         df.dropna(how='all', inplace=True)
#         df.reset_index(drop=True, inplace=True)

#         # Identify the header row containing 'Advance ID'
#         header_row_index = None
#         for idx, row in df.iterrows():
#             if row.astype(str).str.contains('Advance ID', na=False).any():
#                 header_row_index = idx
#                 break

#         if header_row_index is None:
#             raise ValueError("Header row with 'Advance ID' not found.")

#         # The date row is typically one row above the header row
#         date_row_index = header_row_index - 1
#         date_row = df.iloc[date_row_index].fillna('')
#         column_row = df.iloc[header_row_index].fillna('')

#         # Build the column names
#         columns = ['Advance ID', 'Merchant Name']
#         i = 2  # Starting index after 'Advance ID' and 'Merchant Name'

#         while i < len(column_row):
#             # Get the date
#             date = str(date_row[i]).strip()
#             if not date:
#                 # If date is missing, skip the next two columns assuming they belong to the same week
#                 print(f"Warning: Missing date for columns starting at index {i}. Skipping these columns.")
#                 i += 3
#                 continue

#             # Get the column names for this date
#             gross_col = str(column_row[i]).strip()
#             fees_col = str(column_row[i + 1]).strip() if (i + 1) < len(column_row) else ''
#             net_col = str(column_row[i + 2]).strip() if (i + 2) < len(column_row) else ''

#             # Append column names with date
#             if gross_col:
#                 columns.append(f"{gross_col}_{date}")
#             if fees_col:
#                 columns.append(f"{fees_col}_{date}")
#             if net_col:
#                 columns.append(f"{net_col}_{date}")

#             i += 3  # Move to the next set of 3 columns

#         # Check for 'Total' column at the end
#         if i < len(column_row):
#             total_col_name = str(column_row[i]).strip()
#             if total_col_name:
#                 columns.append(total_col_name)

#         # Debugging: Print the number of columns expected vs actual
#         print(f"Number of columns constructed: {len(columns)}")
#         print(f"Number of columns in DataFrame: {len(df.columns)}")

#         # If there's a mismatch, handle it
#         if len(columns) != len(df.columns):
#             # Attempt to adjust by checking if 'Total' was missed
#             if 'Total' not in columns and 'Total' in column_row.values:
#                 columns.append('Total')
#                 print("Added 'Total' column to match the DataFrame.")
#             else:
#                 raise ValueError(f"Length mismatch: Expected {len(columns)} columns, but got {len(df.columns)} columns.")

#         # Assign the constructed column names to the DataFrame
#         df.columns = columns

#         # Remove header rows and rows above
#         df = df.iloc[header_row_index + 1:].reset_index(drop=True)

#         # Remove rows where 'Advance ID' is NaN
#         df = df[df['Advance ID'].notna()]

#         # Remove any 'Total' or 'Grand Total' rows
#         df = df[~df['Advance ID'].astype(str).str.contains('Total', na=False)]

#         # Identify the latest 'Net' column
#         net_columns = [col for col in df.columns if 'Net_' in col]

#         if not net_columns:
#             raise ValueError("No 'Net' columns found in the data.")

#         latest_net_column = net_columns[-1]

#         # Get corresponding 'Gross Payment' and 'Fees' columns
#         latest_net_index = df.columns.get_loc(latest_net_column)
#         latest_gross_column = df.columns[latest_net_index - 2] if (latest_net_index - 2) >= 0 else None
#         latest_fees_column = df.columns[latest_net_index - 1] if (latest_net_index - 1) >= 0 else None

#         if not latest_gross_column or not latest_fees_column:
#             raise ValueError("Could not identify corresponding 'Gross Payment' or 'Fees' columns.")

#         # Extract required columns and create a copy to avoid SettingWithCopyWarning
#         required_columns = [
#             'Advance ID',
#             'Merchant Name',
#             latest_gross_column,
#             latest_net_column,
#             latest_fees_column
#         ]
#         latest_week_df = df[required_columns].copy()

#         # Rename columns
#         latest_week_df = latest_week_df.rename(columns={
#             'Advance ID': 'Funder Advance ID',
#             'Merchant Name': 'Merchant Name',
#             latest_gross_column: 'Sum of Syn Gross Amount',
#             latest_net_column: 'Sum of Syn Net Amount',
#             latest_fees_column: 'Total Servicing Fee'
#         })

#         # Clean currency columns using .loc to avoid SettingWithCopyWarning
#         for col in ['Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee']:
#             latest_week_df.loc[:, col] = latest_week_df[col].apply(currency_to_float)

#         # Replace NaN with 0.00 in currency columns and ensure they are floats
#         latest_week_df[['Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee']] = latest_week_df[['Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee']].fillna(0.00).astype(float)

#         # Verify no NaN values remain in monetary columns
#         if latest_week_df[['Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee']].isna().any().any():
#             print("Warning: There are still NaN values in monetary columns. Replacing them with 0.00.")
#             latest_week_df[['Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee']] = latest_week_df[['Sum of Syn Gross Amount', 'Sum of Syn Net Amount', 'Total Servicing Fee']].fillna(0.00).astype(float)

#         # Remove rows where all amounts are zero
#         latest_week_df = latest_week_df[
#             (latest_week_df['Sum of Syn Gross Amount'] != 0.0) |
#             (latest_week_df['Sum of Syn Net Amount'] != 0.0) |
#             (latest_week_df['Total Servicing Fee'] != 0.0)
#         ]

#         # Round amounts to two decimal places
#         latest_week_df['Sum of Syn Gross Amount'] = latest_week_df['Sum of Syn Gross Amount'].round(2)
#         latest_week_df['Sum of Syn Net Amount'] = latest_week_df['Sum of Syn Net Amount'].round(2)
#         latest_week_df['Total Servicing Fee'] = latest_week_df['Total Servicing Fee'].abs().round(2)

#         # Get the 'Total' row from the original DataFrame
#         total_row = df[df['Advance ID'].astype(str).str.contains('Total', na=False)]

#         if not total_row.empty:
#             total_gross_payment = currency_to_float(total_row[latest_gross_column].values[0])
#             total_net = currency_to_float(total_row[latest_net_column].values[0])
#             total_fees = abs(currency_to_float(total_row[latest_fees_column].values[0]))
#         else:
#             # Calculate totals if 'Total' row is missing
#             total_gross_payment = latest_week_df['Sum of Syn Gross Amount'].sum()
#             total_net = latest_week_df['Sum of Syn Net Amount'].sum()
#             total_fees = latest_week_df['Total Servicing Fee'].sum()

#         # Create and append a totals row
#         totals_row = pd.DataFrame({
#             'Funder Advance ID': ['All'],
#             'Merchant Name': '',
#             'Sum of Syn Gross Amount': [total_gross_payment],
#             'Sum of Syn Net Amount': [total_net],
#             'Total Servicing Fee': [total_fees]
#         })
#         latest_week_df = pd.concat([latest_week_df, totals_row], ignore_index=True)

#         # Save the DataFrame to a CSV file
#         today_date = datetime.now().strftime("%m_%d_%Y")
#         directory = os.path.expanduser(
#             f"{output_path}/{portfolio_name}/{today_date}/Weekly_Pivot_Tables"
#         )
#         os.makedirs(directory, exist_ok=True)
#         output_file = f"VESPER_{today_date}.csv"
#         output_path_full = os.path.join(directory, output_file)
#         latest_week_df.to_csv(output_path_full, index=False)

#         # Return the DataFrame and totals
#         return latest_week_df, total_gross_payment, total_net, total_fees, None


#     except Exception as e:
#         print(f"Error in VESPER parser: {e}")
#         return None, None, None, None, str(e)


# if __name__ == "__main__":
#     # Replace these with your test values
#     file_path = "V.csv"
#     output_path = "./output"  # Set to a valid, writable directory
#     portfolio_name = "Alder"

#     df_output, total_gross_amount, total_net_amount, total_fee, error = parse_vesper(
#         file_path, output_path, portfolio_name
#     )

#     if error:
#         print(f"An error occurred: {error}")
#     else:
#         print("Parsing completed successfully.")
#         print("Output DataFrame:")
#         print(df_output)
#         print(f"Total Gross Amount: {total_gross_amount:.2f}")
#         print(f"Total Net Amount: {total_net_amount:.2f}")
#         print(f"Total Fee: {total_fee:.2f}")






import pandas as pd
from datetime import datetime
import os
from io import StringIO


def parse_VSPR(csv_file, output_path, portfolio_name):
    try:
        # Read the CSV file into a list of lines
        with open(csv_file, 'r') as f:
            lines = f.readlines()
        
        # Remove empty lines
        lines = [line for line in lines if line.strip()]
        
        # Find the header row index by looking for the line that starts with 'Advance ID'
        header_row_index = None
        for idx, line in enumerate(lines):
            if line.strip().startswith('Advance ID'):
                header_row_index = idx
                break

        if header_row_index is None:
            raise ValueError("Header row not found in the CSV file.")

        # Prepare the cleaned CSV data
        cleaned_csv = StringIO(''.join(lines))

        # Read the CSV, setting header to the identified header row
        cleaned_csv.seek(0)
        df = pd.read_csv(cleaned_csv, header=header_row_index)

        # Identify the latest 'Net' column that isn't a 'Total' column
        columns = df.columns.tolist()
        acs_columns = [col for col in columns if "Net" in col and "Total" not in col]
        latest_net_column = acs_columns[-1] if acs_columns else None

        if latest_net_column is None:
            raise ValueError("CSV file format is incorrect or 'Net' columns are missing.")

        # Indexes for the 'Gross Payment' and 'Fees' that align with the latest 'Net' column
        latest_week_index = columns.index(latest_net_column)
        latest_gross_column = columns[latest_week_index - 2]
        latest_fees_column = columns[latest_week_index - 1]

        # Extract relevant columns for the latest week
        latest_week_df = df.iloc[
            :, [0, 1, latest_week_index - 2, latest_week_index, latest_week_index - 1]
        ]

        # Find the 'Grand Total' row using the original 'Advance ID' column
        total_row = df[df["Advance ID"] == "Grand Total"]

        # Rename the columns
        latest_week_df.columns = [
            "Funder Advance ID",
            "Merchant Name",
            "Sum of Syn Gross Amount",
            "Sum of Syn Net Amount",
            "Total Servicing Fee",
        ]

        # Replace NaN with 0.00 and convert to float
        latest_week_df = latest_week_df.fillna(0.00)
        latest_week_df["Sum of Syn Gross Amount"] = (
            latest_week_df["Sum of Syn Gross Amount"]
            .replace(r"[\$,]", "", regex=True)
            .astype(float)
            .round(2)
        )
        latest_week_df["Sum of Syn Net Amount"] = (
            latest_week_df["Sum of Syn Net Amount"]
            .replace(r"[\$,]", "", regex=True)
            .astype(float)
            .round(2)
        )
        latest_week_df["Total Servicing Fee"] = (
            latest_week_df["Total Servicing Fee"]
            .replace(r"[\$,]", "", regex=True)
            .astype(float)
            .abs()
            .round(2)
        )

        # Remove rows with invalid data
        latest_week_df = latest_week_df[
            latest_week_df["Merchant Name"].notna()
            & (latest_week_df["Merchant Name"] != 0.0)
            & (latest_week_df["Sum of Syn Gross Amount"] != 0.0)
            & (latest_week_df["Sum of Syn Net Amount"] != 0.0)
            & (latest_week_df["Total Servicing Fee"] != 0.0)
        ]

        # Get the totals from the 'Grand Total' row
        if not total_row.empty:
            total_gross_payment = total_row[latest_gross_column].values[0]
            total_net = total_row[latest_net_column].values[0]
            total_fees = total_row[latest_fees_column].values[0]

            # Remove dollar signs and convert to float
            total_gross_payment = float(
                str(total_gross_payment).replace("$", "").replace(",", "")
            )
            total_net = float(str(total_net).replace("$", "").replace(",", ""))
            total_fees = abs(float(str(total_fees).replace("$", "").replace(",", "")))
        else:
            total_gross_payment = 0.0
            total_net = 0.0
            total_fees = 0.0

        # Manually create and append a totals row
        totals_row = pd.DataFrame(
            {
                "Funder Advance ID": ["All"],
                "Merchant Name": "",
                "Sum of Syn Gross Amount": [total_gross_payment],
                "Sum of Syn Net Amount": [total_net],
                "Total Servicing Fee": [total_fees],
            }
        )
        latest_week_df = pd.concat([latest_week_df, totals_row], ignore_index=True)

        # Include the current date in the filename for saving the CSV
        today_date = datetime.now().strftime("%m_%d_%Y")

        # Specify the directory
        directory = os.path.expanduser(
            f"{output_path}/{portfolio_name}/{today_date}/Weekly_Pivot_Tables"
        )

        # Create the directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Create the output filename
        output_file = f"ACS_{today_date}.csv"

        # Construct the full path to the output file
        output_path = os.path.join(directory, output_file)

        # Save the DataFrame to the CSV file
        latest_week_df.to_csv(output_path, index=False)

        # Return the DataFrame and totals
        return latest_week_df, total_gross_payment, total_net, total_fees, None

    except Exception as e:
        print(f"Error in ACS parser: {e}")
        return None, None, None, None, str(e)
