


# def get_workbook_data(workbook_bytes, selected_file, output_path, portfolio_name):
#     if isinstance(workbook_bytes, list):
#         workbook_bytes = b"".join(workbook_bytes)
    
#     if portfolio_name == 1:
#         portfolio_name = "Alder"
#     elif portfolio_name == 2:
#         portfolio_name = "White Rabbit"

#     workbook = load_workbook(filename=io.BytesIO(workbook_bytes))

#     # Save a copy of the workbook to local machine
#     current_date = datetime.now()
#     date_string = current_date.strftime("%m_%d_%Y")
#     os.makedirs(
#         os.path.expanduser(f"{output_path}/{portfolio_name}/{date_string}"),
#         exist_ok=True,
#     )
#     file_name = selected_file.removesuffix(".xlsx")
#     file_path_backup = os.path.expanduser(
#         f"{output_path}/{portfolio_name}/{date_string}/{file_name}_BACKUP_{date_string}.xlsx"
#     )

#     with open(file_path_backup, "wb") as file:
#         file.write(workbook_bytes)

#     return workbook

# # Function to add a column if the current Friday's Net RTR column does not exist
# def add_net_rtr_column_if_needed(worksheet, selected_date=None, header_row=2):
#     if selected_date:
#         month_day = selected_date.strftime("%-m/%-d")
#     else:
#         current_friday = datetime.now() + timedelta((4 - datetime.now().weekday()) % 7)
#         month_day = current_friday.strftime("%-m/%-d")

#     rtr_balance_column = None
#     net_rtr_column_index = None

#     # Find the R&H Net RTR Balance column index
#     for idx, cell in enumerate(worksheet[header_row]):
#         if cell.value and "R&H Net RTR Balance" in cell.value:
#             rtr_balance_column = idx + 1  # Excel is 1-indexed
#             break

#     # Check if the column for the selected date already exists
#     for idx, cell in enumerate(worksheet[header_row]):
#         if cell.value and f"Net RTR {month_day}" == cell.value:
#             net_rtr_column_index = idx + 1  # Excel is 1-indexed
#             break

#     # If no RTR balance column found, something is wrong with the sheet format
#     if rtr_balance_column is None:
#         raise ValueError("R&H Net RTR Balance column not found in the sheet.")

#     # If the Net RTR column for the selected date doesn't exist, we insert it before the R&H Net RTR Balance column
#     if net_rtr_column_index is None:
#         worksheet.insert_cols(rtr_balance_column)
#         net_rtr_column_index = rtr_balance_column

#         # Set the value for the header of the new column
#         worksheet.cell(row=header_row, column=net_rtr_column_index).value = (
#             f"Net RTR {month_day}"
#         )

#         # Set the worksheet name in the first row of the new column
#         worksheet.cell(row=1, column=net_rtr_column_index).value = worksheet.title

#         # Copy formatting from the cell one column to the left for each cell in the new column
#         for row in range(1, worksheet.max_row + 1):
#             left_cell = worksheet.cell(row=row, column=net_rtr_column_index - 1)
#             new_cell = worksheet.cell(row=row, column=net_rtr_column_index)

#             new_cell.font = copy(left_cell.font)
#             new_cell.border = copy(left_cell.border)
#             new_cell.fill = copy(left_cell.fill)
#             new_cell.number_format = copy(left_cell.number_format)
#             new_cell.protection = copy(left_cell.protection)
#             new_cell.alignment = copy(left_cell.alignment)

#     added_col = get_column_letter(net_rtr_column_index)

#     update_total_net_rtr_formula(worksheet, added_col)

#     return added_col

# def update_total_net_rtr_formula(worksheet, net_rtr_column, header_row=2):
#     # Find the column letter for the "Total Net RTR Payment Received" column
#     total_net_rtr_header = "Total Net RTR Payment Received"
#     total_net_rtr_column = None
#     for cell in worksheet[header_row]:
#         if cell.value == total_net_rtr_header:
#             total_net_rtr_column = openpyxl.utils.get_column_letter(cell.column)
#             break

#     # If the "Total Net RTR Payment Received" column is not found, return
#     if total_net_rtr_column is None:
#         return

#     # Get the column number for the "Total Net RTR Payment Received" column
#     total_net_rtr_column_number = openpyxl.utils.column_index_from_string(
#         total_net_rtr_column
#     )

#     # Get the column number for the newly inserted Net RTR column
#     net_rtr_column_number = openpyxl.utils.column_index_from_string(net_rtr_column)

#     # Update the formula for each row in the "Total Net RTR Payment Received" column
#     start_column = openpyxl.utils.get_column_letter(total_net_rtr_column_number + 1)
#     for row in range(header_row + 1, worksheet.max_row + 1):
#         cell = worksheet[f"{total_net_rtr_column}{row}"]
#         formula = f"=SUM({start_column}{row}:{net_rtr_column}{row})"
#         cell.value = formula


# def map_net_amount_to_excel(
#     worksheet, df_csv, net_rtr_column, output_path, portfolio_name, header_row=2
# ):
#     advance_id_to_row = {}
#     # Adjust to column 'E' for 'Funder Advance ID'
#     for row in worksheet.iter_rows(min_row=header_row + 1, min_col=5, max_col=5):
#         cell = row[0]
#         if cell.value:
#             # Convert cell value to string, strip whitespace, and store it with its row number
#             advance_id_to_row[str(cell.value).strip()] = cell.row

#     # Mapping using 'Funder Advance ID'
#     for index, row in df_csv.iterrows():
#         advance_id = str(row["Funder Advance ID"]).strip()

#         # Skip processing if 'Funder Advance ID' is 'All'
#         if advance_id == "All":
#             continue

#         net_amount = row["Sum of Syn Net Amount"]

#         if advance_id in advance_id_to_row:
#             excel_row_num = advance_id_to_row[advance_id]
#             cell_reference = f"{net_rtr_column}{excel_row_num}"
#             worksheet[cell_reference].value = net_amount
#             log_to_file(
#                 f"Advance ID '{advance_id}' mapped to row {excel_row_num} with net amount {net_amount}.",
#                 output_path,
#                 portfolio_name,
#             )
#         else:
#             log_to_file(
#                 f"Funder Advance ID '{advance_id}' not found in Excel sheet.",
#                 output_path,
#                 portfolio_name,
#             )

# def add_data_to_sheet(
#     workbook, df, sheet_name, output_path, portfolio_name, selected_date=None
# ):
#     try:
#         sheet = workbook[sheet_name]
#         log_to_file(f"Adding data to sheet '{sheet_name}'...", output_path, portfolio_name)
#         print(f"Adding data to sheet '{sheet_name}'...")  # Debugging statement

#         # Extract Advance IDs and Merchant Names from DataFrame
#         df_advance_ids = (
#             df[["Funder Advance ID", "Merchant Name"]]
#             .dropna(subset=["Funder Advance ID"])
#             .set_index("Funder Advance ID")
#             .to_dict("index")
#         )

#         # Extract Advance IDs from Excel worksheet
#         worksheet_advance_ids = {
#             str(m[0]).strip(): m
#             for m in sheet.iter_rows(min_col=4, max_col=5, values_only=True)
#             if m[0]
#         }

#         # Find unmatched Advance IDs and corresponding Merchant Names
#         unmatched_advance_ids = set(df_advance_ids) - set(worksheet_advance_ids)
#         unmatched_info = {
#             aid: df_advance_ids[aid]["Merchant Name"]
#             for aid in unmatched_advance_ids
#             if aid != "All" and df_advance_ids[aid]["Merchant Name"] != "All"
#         }

#         # Format unmatched info for logging
#         formatted_unmatched_info = ", ".join(
#             f"{aid}: {info}" for aid, info in unmatched_info.items()
#         )
#         detailed_unmatched_info = [
#             {"sheet_name": sheet_name, "advance_id": aid, "merchant_name": info}
#             for aid, info in unmatched_info.items()
#         ]

#         log_to_file(
#             f"Advance IDs and Merchants not found in Excel sheet: {formatted_unmatched_info}",
#             output_path,
#             portfolio_name,
#         )

#         # Ensure the Net RTR column is added and get its column letter
#         net_rtr_column = add_net_rtr_column_if_needed(sheet, selected_date)
#         print(f"net_rtr_column: {net_rtr_column}")  # Debugging statement

#         # Updated to map using 'Advance ID'
#         map_net_amount_to_excel(sheet, df, net_rtr_column, output_path, portfolio_name)

#         # Save changes to the workbook
#         output_bytes = BytesIO()
#         workbook.save(output_bytes)
#         output_bytes.seek(0)
#         final_bytes = output_bytes.getvalue()
#         print(f"final_bytes length: {len(final_bytes)}")  # Debugging statement
#         if not final_bytes:
#             raise ValueError("final_bytes is None or empty")

#         return final_bytes, detailed_unmatched_info
#     except Exception as e:
#         print(f"Error in add_data_to_sheet: {str(e)}")
#         log_to_file(f"Error in add_data_to_sheet: {str(e)}", output_path, portfolio_name)
#         return None, []

from openpyxl import load_workbook
import openpyxl
import io
import os
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
from io import BytesIO
from copy import copy
from log import log_to_file


import io
import os
from datetime import datetime, timedelta
from copy import copy
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from io import BytesIO
from log import log_to_file


def get_workbook_data(workbook_bytes, selected_file, output_path, portfolio_name):
    if isinstance(workbook_bytes, list):
        workbook_bytes = b"".join(workbook_bytes)

    portfolio_name = {1: "Alder", 2: "White Rabbit"}.get(portfolio_name, portfolio_name)

    workbook = load_workbook(filename=io.BytesIO(workbook_bytes))

    current_date = datetime.now()
    date_string = current_date.strftime("%m_%d_%Y")
    os.makedirs(
        os.path.expanduser(f"{output_path}/{portfolio_name}/{date_string}"),
        exist_ok=True,
    )
    file_name = selected_file.removesuffix(".xlsx")
    file_path_backup = os.path.expanduser(
        f"{output_path}/{portfolio_name}/{date_string}/{file_name}_BACKUP_{date_string}.xlsx"
    )

    with open(file_path_backup, "wb") as file:
        file.write(workbook_bytes)

    return workbook


def add_net_rtr_column_if_needed(worksheet, selected_date=None, header_row=2):
    month_day = (
        selected_date.strftime("%-m/%-d")
        if selected_date
        else (datetime.now() + timedelta((4 - datetime.now().weekday()) % 7)).strftime(
            "%-m/%-d"
        )
    )

    rtr_balance_column = None
    net_rtr_column_index = None

    for idx, cell in enumerate(worksheet[header_row]):
        if cell.value and "R&H Net RTR Balance" in cell.value:
            rtr_balance_column = idx + 1  # Excel is 1-indexed
            break

    for idx, cell in enumerate(worksheet[header_row]):
        if cell.value and f"Net RTR {month_day}" == cell.value:
            net_rtr_column_index = idx + 1  # Excel is 1-indexed
            break

    if rtr_balance_column is None:
        raise ValueError("R&H Net RTR Balance column not found in the sheet.")

    if net_rtr_column_index is None:
        worksheet.insert_cols(rtr_balance_column)
        net_rtr_column_index = rtr_balance_column

        worksheet.cell(row=header_row, column=net_rtr_column_index).value = (
            f"Net RTR {month_day}"
        )
        worksheet.cell(row=1, column=net_rtr_column_index).value = worksheet.title

        for row in range(1, worksheet.max_row + 1):
            left_cell = worksheet.cell(row=row, column=net_rtr_column_index - 1)
            new_cell = worksheet.cell(row=row, column=net_rtr_column_index)

            new_cell.font = copy(left_cell.font)
            new_cell.border = copy(left_cell.border)
            new_cell.fill = copy(left_cell.fill)
            new_cell.number_format = copy(left_cell.number_format)
            new_cell.protection = copy(left_cell.protection)
            new_cell.alignment = copy(left_cell.alignment)

    added_col = get_column_letter(net_rtr_column_index)
    update_total_net_rtr_formula(worksheet, added_col)

    return added_col


def update_total_net_rtr_formula(worksheet, net_rtr_column, header_row=2):
    total_net_rtr_header = "Total Net RTR Payment Received"
    total_net_rtr_column = None
    for cell in worksheet[header_row]:
        if cell.value == total_net_rtr_header:
            total_net_rtr_column = get_column_letter(cell.column)
            break

    if total_net_rtr_column is None:
        return

    start_column = get_column_letter(openpyxl.utils.column_index_from_string(total_net_rtr_column) + 1)
    for row in range(header_row + 1, worksheet.max_row + 1):
        formula = f"=SUM({start_column}{row}:{net_rtr_column}{row})"
        worksheet[f"{total_net_rtr_column}{row}"].value = formula


def map_net_amount_to_excel(
    worksheet, df_csv, net_rtr_column, output_path, portfolio_name, header_row=2
):
    advance_id_to_row = {
        str(cell.value).strip(): cell.row
        for cell in worksheet.iter_rows(min_row=header_row + 1, min_col=5, max_col=5)
        if cell[0].value
    }

    for _, row in df_csv.iterrows():
        advance_id = str(row["Funder Advance ID"]).strip()
        if advance_id == "All":
            continue

        net_amount = row["Sum of Syn Net Amount"]
        if advance_id in advance_id_to_row:
            excel_row_num = advance_id_to_row[advance_id]
            worksheet[f"{net_rtr_column}{excel_row_num}"].value = net_amount
            log_to_file(
                f"Advance ID '{advance_id}' mapped to row {excel_row_num} with net amount {net_amount}.",
                output_path,
                portfolio_name,
            )
        else:
            log_to_file(
                f"Funder Advance ID '{advance_id}' not found in Excel sheet.",
                output_path,
                portfolio_name,
            )

def add_data_to_sheet(
    workbook, df, sheet_name, output_path, portfolio_name, selected_date=None
):
    try:
        sheet = workbook[sheet_name]
        log_to_file(f"Adding data to sheet '{sheet_name}'...", output_path, portfolio_name)
        print(f"Adding data to sheet '{sheet_name}'...")  # Debugging statement

        # Extract Advance IDs and Merchant Names from DataFrame
        df_advance_ids = (
            df[["Funder Advance ID", "Merchant Name"]]
            .dropna(subset=["Funder Advance ID"])
            .set_index("Funder Advance ID")
            .to_dict("index")
        )
        print(f"df_advance_ids: {df_advance_ids}")  # Debugging statement

        # Extract Advance IDs from Excel worksheet
        worksheet_advance_ids = {
            str(m[0]).strip(): m
            for m in sheet.iter_rows(min_col=4, max_col=5, values_only=True)
            if m[0]
        }
        print(f"worksheet_advance_ids: {worksheet_advance_ids}")  # Debugging statement

        # Find unmatched Advance IDs and corresponding Merchant Names
        unmatched_advance_ids = set(df_advance_ids) - set(worksheet_advance_ids)
        unmatched_info = {
            aid: df_advance_ids[aid]["Merchant Name"]
            for aid in unmatched_advance_ids
            if aid != "All" and df_advance_ids[aid]["Merchant Name"] != "All"
        }

        # Format unmatched info for logging
        formatted_unmatched_info = ", ".join(
            f"{aid}: {info}" for aid, info in unmatched_info.items()
        )
        detailed_unmatched_info = [
            {"sheet_name": sheet_name, "advance_id": aid, "merchant_name": info}
            for aid, info in unmatched_info.items()
        ]

        log_to_file(
            f"Advance IDs and Merchants not found in Excel sheet: {formatted_unmatched_info}",
            output_path,
            portfolio_name,
        )

        # Ensure the Net RTR column is added and get its column letter
        net_rtr_column = add_net_rtr_column_if_needed(sheet, selected_date)
        print(f"net_rtr_column: {net_rtr_column}")  # Debugging statement

        # Updated to map using 'Advance ID'
        map_net_amount_to_excel(sheet, df, net_rtr_column, output_path, portfolio_name)

        # Save changes to the workbook
        output_bytes = BytesIO()
        workbook.save(output_bytes)
        output_bytes.seek(0)
        final_bytes = output_bytes.getvalue()
        print(f"final_bytes length: {len(final_bytes)}")  # Debugging statement
        if not final_bytes:
            raise ValueError("final_bytes is None or empty")

        return final_bytes, detailed_unmatched_info
    except Exception as e:
        error_message = f"Error in add_data_to_sheet: {str(e)}"
        print(error_message)
        log_to_file(error_message, output_path, portfolio_name)
        return None, []
