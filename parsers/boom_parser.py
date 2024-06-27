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
        if len(missing_columns) > 3:
            message += ", ..."
        raise ValueError(message)


def parse_boom(csv_file, output_path, portfolio_name):
    try:
        df = pd.read_csv(csv_file)
        expected_boom_columns = [
            "Business Name",
            "Payable Amt (Gross)",
            "Servicing Fee $",
            "Payable Amt (Net)",
            "Syndicators Name",
            "Payable Cleared Date",
            "Payable Status",
            "Advance ID",
            "Funding Date",
            "Debit Amount",
            "Debit Cleared Date",
            "Debit Date",
            "Debit Status",
        ]
        validate_csv_columns(df, expected_boom_columns)
        df["Payable Amt (Gross)"] = (
            df["Payable Amt (Gross)"].replace(r"[\$,]", "", regex=True).astype(float)
        )
        df["Payable Amt (Net)"] = (
            df["Payable Amt (Net)"].replace(r"[\$,]", "", regex=True).astype(float)
        )
        df["Servicing Fee $"] = (
            df["Servicing Fee $"].replace(r"[\$,]", "", regex=True).astype(float)
        )

        pivot_table = pd.pivot_table(
            df,
            values=["Payable Amt (Gross)", "Payable Amt (Net)", "Servicing Fee $"],
            index=["Advance ID", "Business Name"],
            aggfunc={
                "Payable Amt (Gross)": "sum",
                "Payable Amt (Net)": "sum",
                "Servicing Fee $": "sum",
            },
            margins=True,
        ).round(2)

        pivot_table.columns = [
            "Sum of Syn Gross Amount",
            "Sum of Syn Net Amount",
            "Total Servicing Fee",
        ]
        pivot_table = pivot_table.reset_index().rename(
            columns={
                "Advance ID": "Funder Advance ID",
                "Business Name": "Merchant Name",
            }
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
        output_file = f"BOOM_{today_date}.csv"
        output_path = os.path.join(directory, output_file)
        pivot_table.to_csv(output_path, index=False)

        totals_row = pivot_table[pivot_table["Funder Advance ID"] == "All"]
        total_gross_amount = totals_row["Sum of Syn Gross Amount"].values[0]
        total_net_amount = totals_row["Sum of Syn Net Amount"].values[0]
        total_fee = totals_row["Total Servicing Fee"].values[0]

        return pivot_table, total_gross_amount, total_net_amount, total_fee, None

    except Exception as e:
        print(f"Error in BOOM parser: {e}")
        return None, None, None, None, str(e)
