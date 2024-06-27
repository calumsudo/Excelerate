# import pandas as pd
# from datetime import datetime
# import os


# def parse_acs(csv_file, output_path, portfolio_name):
#     try:
#         # Set the starting row based on the portfolio name
#         start_row = 2

#         # Read the CSV file, skipping the appropriate rows and setting the header
#         df = pd.read_csv(csv_file, header=start_row)

#         # Identify the latest 'Net' column that isn't a 'Total' column
#         columns = df.columns.tolist()
#         acs_columns = [col for col in columns if "Net" in col and "Total" not in col]
#         latest_net_column = acs_columns[-1] if acs_columns else None

#         if latest_net_column is None:
#             raise ValueError("CSV file format")

#         # Indexes for the 'Gross Payment' and 'Fees' that align with the latest 'Net' column
#         latest_week_index = columns.index(latest_net_column)
#         latest_gross_column = columns[latest_week_index - 2]
#         latest_fees_column = columns[latest_week_index - 1]

#         # Extract relevant columns for the latest week, switching the order of 'Fees' and 'Net'
#         latest_week_df = df.iloc[
#             :, [0, 1, latest_week_index - 2, latest_week_index, latest_week_index - 1]
#         ]

#         # Find the 'Grand Total' row using the original 'Advance ID' column
#         total_row = df[df["Advance ID"] == "Grand Total"]

#         # Rename the columns
#         latest_week_df.columns = [
#             "Funder Advance ID",
#             "Merchant Name",
#             "Sum of Syn Gross Amount",
#             "Sum of Syn Net Amount",
#             "Total Servicing Fee",
#         ]

#         # Replace NaN with 0.00 and convert to float
#         latest_week_df = latest_week_df.fillna(0.00)
#         latest_week_df.loc[:, "Sum of Syn Gross Amount"] = (
#             latest_week_df["Sum of Syn Gross Amount"]
#             .replace("[\$,]", "", regex=True)
#             .astype(float)
#             .round(2)
#         )
#         latest_week_df.loc[:, "Sum of Syn Net Amount"] = (
#             latest_week_df["Sum of Syn Net Amount"]
#             .replace("[\$,]", "", regex=True)
#             .astype(float)
#             .round(2)
#         )
#         latest_week_df.loc[:, "Total Servicing Fee"] = (
#             latest_week_df["Total Servicing Fee"]
#             .replace("[\$,]", "", regex=True)
#             .astype(float)
#             .abs()
#             .round(2)
#         )

#         # Remove rows with Merchant Name as NaN, empty, or 0.0
#         latest_week_df = latest_week_df[
#             (latest_week_df["Merchant Name"].notna())
#             & (latest_week_df["Merchant Name"] != 0.0)
#             & (latest_week_df["Sum of Syn Gross Amount"] != 0.0)
#             & (latest_week_df["Sum of Syn Net Amount"] != 0.0)
#             & (latest_week_df["Total Servicing Fee"] != 0.0)
#         ]

#         # Get the totals from the 'Grand Total' row
#         if not total_row.empty:
#             total_gross_payment = total_row[latest_gross_column].values[0]
#             total_net = total_row[latest_net_column].values[0]
#             total_fees = total_row[latest_fees_column].values[0]

#             # Remove dollar signs and convert to float
#             total_gross_payment = float(
#                 str(total_gross_payment).replace("$", "").replace(",", "")
#             )
#             total_net = float(str(total_net).replace("$", "").replace(",", ""))
#             total_fees = abs(float(str(total_fees).replace("$", "").replace(",", "")))
#         else:
#             total_gross_payment = 0.0
#             total_net = 0.0
#             total_fees = 0.0

#         # Manually create and append a totals row
#         totals_row = pd.DataFrame(
#             {
#                 "Funder Advance ID": ["All"],
#                 "Merchant Name": "",
#                 "Sum of Syn Gross Amount": [total_gross_payment],
#                 "Sum of Syn Net Amount": [total_net],
#                 "Total Servicing Fee": [total_fees],
#             }
#         )
#         latest_week_df = pd.concat([latest_week_df, totals_row], ignore_index=True)

#         # Include the current date in the filename for saving the CSV
#         today_date = datetime.now().strftime("%m_%d_%Y")

#         # Specify the directory
#         directory = os.path.expanduser(
#             f"{output_path}/{portfolio_name}/{today_date}/Weekly_Pivot_Tables"
#         )

#         # Create the directory if it doesn't exist
#         os.makedirs(directory, exist_ok=True)

#         # Create the output name
#         output_file = f"ACS_{today_date}.csv"

#         # Construct the full path to the output file
#         output_path = os.path.join(directory, output_file)

#         # Save the DataFrame to the CSV file
#         latest_week_df.to_csv(output_path, index=False)

#         # Return the DataFrame and totals
#         return latest_week_df, total_gross_payment, total_net, total_fees, None

#     except Exception as e:
#         return None, None, None, None, str(e)


import pandas as pd
from datetime import datetime
import os

def parse_acs(csv_file, output_path, portfolio_name):
    try:
        # Set the starting row based on the portfolio name
        start_row = 2

        # Read the CSV file, skipping the appropriate rows and setting the header
        df = pd.read_csv(csv_file, header=start_row)

        # Identify the latest 'Net' column that isn't a 'Total' column
        columns = df.columns.tolist()
        acs_columns = [col for col in columns if "Net" in col and "Total" not in col]
        latest_net_column = acs_columns[-1] if acs_columns else None

        if latest_net_column is None:
            raise ValueError("CSV file format")

        # Indexes for the 'Gross Payment' and 'Fees' that align with the latest 'Net' column
        latest_week_index = columns.index(latest_net_column)
        latest_gross_column = columns[latest_week_index - 2]
        latest_fees_column = columns[latest_week_index - 1]

        # Extract relevant columns for the latest week, switching the order of 'Fees' and 'Net'
        latest_week_df = df.iloc[:, [0, 1, latest_week_index - 2, latest_week_index, latest_week_index - 1]]

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
            .replace("[\$,]", "", regex=True)
            .astype(float)
            .round(2)
        )
        latest_week_df["Sum of Syn Net Amount"] = (
            latest_week_df["Sum of Syn Net Amount"]
            .replace("[\$,]", "", regex=True)
            .astype(float)
            .round(2)
        )
        latest_week_df["Total Servicing Fee"] = (
            latest_week_df["Total Servicing Fee"]
            .replace("[\$,]", "", regex=True)
            .astype(float)
            .abs()
            .round(2)
        )

        # Remove rows with Merchant Name as NaN, empty, or 0.0
        latest_week_df = latest_week_df[
            (latest_week_df["Merchant Name"].notna())
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
            total_gross_payment = float(str(total_gross_payment).replace("$", "").replace(",", "").strip())
            total_net = float(str(total_net).replace("$", "").replace(",", "").strip())
            total_fees = abs(float(str(total_fees).replace("$", "").replace(",", "").strip()))
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
        directory = os.path.expanduser(f"{output_path}/{portfolio_name}/{today_date}/Weekly_Pivot_Tables")

        # Create the directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Create the output name
        output_file = f"ACS_{today_date}.csv"

        # Construct the full path to the output file
        output_path = os.path.join(directory, output_file)

        # Save the DataFrame to the CSV file
        latest_week_df.to_csv(output_path, index=False)

        # Return the DataFrame and totals
        return latest_week_df, total_gross_payment, total_net, total_fees, None

    except Exception as e:
        return None, None, None, None, str(e)

