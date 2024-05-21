# import pandas as pd
# from datetime import datetime
# import os


# def validate_csv_columns(df, required_columns):
#     missing_columns = [
#         column for column in required_columns if column not in df.columns
#     ]
#     if missing_columns:
#         limited_missing_columns = missing_columns[:3]
#         message = f"the following columns: {', '.join(limited_missing_columns)}"
#         if len(missing_columns) > 5:
#             message += ", ..."
#         raise ValueError(message)


# def currency_to_float(value):
#     if isinstance(value, str):
#         value = (
#             value.replace("$", "").replace(",", "").replace("(", "-").replace(")", "")
#         )
#     return float(value)


# def parse_bhb(file_path, output_path, portfolio_name):
#     try:
#         if file_path.endswith(".xlsx"):
#             # Read XLSX file
#             df = pd.read_excel(file_path, sheet_name="Sheet1")
#         elif file_path.endswith(".csv"):
#             # Read CSV file
#             df = pd.read_csv(file_path)
#         else:
#             raise ValueError(
#                 "Unsupported file format. Please provide an XLSX or CSV file."
#             )

#         expected_bhb_columns = [
#             "Deal ID",
#             "Deal Name",
#             "Participator Gross Amount",
#             "Non Qualifying Collections",
#             "Total Reversals",
#             "Fee",
#             "Res. Commission",
#             "Net Payment Amount",
#             "Balance",
#         ]

#         validate_csv_columns(df, expected_bhb_columns)

#         df = df[pd.to_numeric(df["Deal ID"], errors="coerce").notnull()]

#         currency_columns = ["Participator Gross Amount", "Net Payment Amount", "Fee"]
#         for column in currency_columns:
#             df[column] = df[column].apply(currency_to_float)

#         pivot_table = pd.pivot_table(
#             df,
#             values=currency_columns,
#             index=["Deal ID", "Deal Name"],
#             aggfunc="sum",
#             margins=True,
#         ).round(2)

#         pivot_table.columns = [
#             "Sum of Syn Gross Amount",
#             "Sum of Syn Net Amount",
#             "Total Servicing Fee",
#         ]
#         pivot_table = pivot_table.reset_index().rename(
#             columns={"Deal ID": "Funder Advance ID", "Deal Name": "Merchant Name"}
#         )
#         pivot_table = pivot_table.reindex(
#             columns=[
#                 "Funder Advance ID",
#                 "Merchant Name",
#                 "Sum of Syn Gross Amount",
#                 "Sum of Syn Net Amount",
#                 "Total Servicing Fee",
#             ]
#         )

#         today_date = datetime.now().strftime("%m_%d_%Y")
#         directory = os.path.expanduser(
#             f"{output_path}/{portfolio_name}/{today_date}/Weekly_Pivot_Tables"
#         )
#         os.makedirs(directory, exist_ok=True)
#         output_file = f"BHB_{today_date}.csv"
#         output_path = os.path.join(directory, output_file)
#         pivot_table.to_csv(output_path, index=False)

#         totals_row = pivot_table[pivot_table["Funder Advance ID"] == "All"]
#         total_gross_amount = totals_row["Sum of Syn Gross Amount"].values[0]
#         total_net_amount = totals_row["Sum of Syn Net Amount"].values[0]
#         total_fee = totals_row["Total Servicing Fee"].values[0]

#         return pivot_table, total_gross_amount, total_net_amount, total_fee, None

#     except Exception as e:
#         return None, None, None, None, str(e)


import pandas as pd
from datetime import datetime
import os


def validate_csv_columns(df, required_columns):
    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]
    if missing_columns:
        limited_missing_columns = missing_columns[:3]
        message = f"the following columns: {', '.join(limited_missing_columns)}"
        if len(missing_columns) > 5:
            message += ", ..."
        raise ValueError(message)


def currency_to_float(value):
    if isinstance(value, str):
        value = (
            value.replace("$", "").replace(",", "").replace("(", "-").replace(")", "")
        )
    return float(value)


def parse_bhb(file_path, output_path, portfolio_name):
    try:
        if file_path.endswith(".xlsx"):
            # Read XLSX file
            df = pd.read_excel(file_path, sheet_name="Sheet1")
        elif file_path.endswith(".csv"):
            # Read CSV file
            df = pd.read_csv(file_path, encoding='utf-8')
        else:
            raise ValueError(
                "Unsupported file format. Please provide an XLSX or CSV file."
            )

        expected_bhb_columns = [
            "Deal ID",
            "Deal Name",
            "Participator Gross Amount",
            "Non Qualifying Collections",
            "Total Reversals",
            "Fee",
            "Res. Commission",
            "Net Payment Amount",
            "Balance",
        ]

        validate_csv_columns(df, expected_bhb_columns)

        df = df[pd.to_numeric(df["Deal ID"], errors="coerce").notnull()]

        currency_columns = ["Participator Gross Amount", "Net Payment Amount", "Fee"]
        for column in currency_columns:
            df[column] = df[column].apply(currency_to_float)

        pivot_table = pd.pivot_table(
            df,
            values=currency_columns,
            index=["Deal ID", "Deal Name"],
            aggfunc="sum",
            margins=True,
        ).round(2)

        pivot_table.columns = [
            "Sum of Syn Gross Amount",
            "Sum of Syn Net Amount",
            "Total Servicing Fee",
        ]
        pivot_table = pivot_table.reset_index().rename(
            columns={"Deal ID": "Funder Advance ID", "Deal Name": "Merchant Name"}
        )
        pivot_table = pivot_table.reindex(
            columns=[
                "Funder Advance ID",
                "Merchant Name",
                "Sum of Syn Gross Amount",
                "Sum of Syn Net Amount",
                "Total Servicing Fee",
            ]
        )

        today_date = datetime.now().strftime("%m_%d_%Y")
        directory = os.path.expanduser(
            f"{output_path}/{portfolio_name}/{today_date}/Weekly_Pivot_Tables"
        )
        os.makedirs(directory, exist_ok=True)
        output_file = f"BHB_{today_date}.csv"
        output_path = os.path.join(directory, output_file)
        pivot_table.to_csv(output_path, index=False, encoding='utf-8')

        totals_row = pivot_table[pivot_table["Funder Advance ID"] == "All"]
        total_gross_amount = totals_row["Sum of Syn Gross Amount"].values[0]
        total_net_amount = totals_row["Sum of Syn Net Amount"].values[0]
        total_fee = totals_row["Total Servicing Fee"].values[0]

        return pivot_table, total_gross_amount, total_net_amount, total_fee, None

    except Exception as e:
        return None, None, None, None, str(e)
