from openpyxl import load_workbook
import openpyxl
import io
import os
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO


def get_workbook_data(workbook_bytes, selected_file, output_path):

    workbook = load_workbook(filename=io.BytesIO(workbook_bytes))

    # Save a copy of the workbook to local machine
    current_date = datetime.now()
    date_string = current_date.strftime("%m_%d_%Y")
    os.makedirs(os.path.expanduser(f"{output_path}/{date_string}"), exist_ok=True)
    file_name = selected_file.removesuffix(".xlsx")
    file_path_backup = os.path.expanduser(f"{output_path}/{date_string}/{file_name}_BACKUP_{date_string}.xlsx")

    with open(file_path_backup, "wb") as file:
        file.write(workbook_bytes)

    return workbook


def find_duplicates_in_column(worksheet, column='B'):
    values = {}
    duplicates = set()
    for row in worksheet.iter_rows(min_col=2, max_col=2, values_only=True):
        merchant = row[0]
        # Convert merchant to string and strip whitespace before checking
        if merchant and str(merchant).strip():
            merchant = str(merchant).strip()  # Ensure merchant is treated as a stripped string
            if merchant in values:
                duplicates.add(merchant)
            else:
                values[merchant] = True
    return list(duplicates)

# Function to add a column if the current Friday's Net RTR column does not exist
def add_net_rtr_column_if_needed(worksheet, header_row=2):
    current_friday = (datetime.now() + timedelta((4 - datetime.now().weekday()) % 7)).strftime('%m/%d')
    rtr_balance_column = None
    net_rtr_column_index = None
    
    # Find the R&H Net RTR Balance column index
    for idx, cell in enumerate(worksheet[header_row]):
        if cell.value and "R&H Net RTR Balance" in cell.value:
            rtr_balance_column = idx + 1  # Excel is 1-indexed
            break

    # Check if the column for the current Friday already exists
    for idx, cell in enumerate(worksheet[header_row]):
        if cell.value and f'Net RTR {current_friday}' == cell.value:
            net_rtr_column_index = idx + 1  # Excel is 1-indexed
            break

    # If no RTR balance column found, something is wrong with the sheet format
    if rtr_balance_column is None:
        raise ValueError("R&H Net RTR Balance column not found in the sheet.")

    # If the Net RTR column for the current Friday doesn't exist, we insert it before the R&H Net RTR Balance column
    if net_rtr_column_index is None:
        worksheet.insert_cols(rtr_balance_column)
        net_rtr_column_index = rtr_balance_column
        # Set the value for the header of the new column
        worksheet.cell(row=header_row, column=rtr_balance_column).value = f'Net RTR {current_friday}'
        
    return get_column_letter(net_rtr_column_index)

def update_total_net_rtr_formula(worksheet, net_rtr_column):
    total_net_rtr_header = "Total Net RTR Payment Received"
    header_row = 2  # Assuming headers are in the second row
    
    # Iterate through cells in the header row without using values_only=True
    for cell in worksheet[header_row]:
        # Now cell is a Cell object, and you can access cell.value
        if cell.value == total_net_rtr_header:
            # Now correctly access the cell's attributes
            # Find the column letter for the cell
            col_letter = openpyxl.utils.get_column_letter(cell.column)
            # Update the formula for the entire column starting from the next row of the header
            for row in range(header_row + 1, worksheet.max_row + 1):
                formula_cell = f'{col_letter}{row}'
                # Assuming you want to sum from AG (column 33) to the new Net RTR column for each row
                start_column_letter = openpyxl.utils.get_column_letter(33)  # AG column
                end_column_letter = net_rtr_column
                worksheet[formula_cell].value = f'=SUM({start_column_letter}{row}:{end_column_letter}{row})'
            break  # Exit loop after updating

# Function to map 'Sum of Syn Net Amount' from CSV to Excel
def map_net_amount_to_excel(worksheet, df_csv, net_rtr_column, header_row=2):
    merchant_to_row = {}
    # We need to iterate without 'values_only' to access the 'row' attribute of Cell objects.
    for row in worksheet.iter_rows(min_row=header_row + 1, min_col=2, max_col=2):  # Adjust min_col and max_col to target Column B
        cell = row[0]  # This is the first cell in the row, which corresponds to Column B
        if cell.value:  # Make sure the cell has a value
            merchant_to_row[cell.value.strip()] = cell.row  # Map the merchant name to its row number

    # Now, let's loop through the DataFrame and assign values in Excel
    for index, row in df_csv.iterrows():
        merchant_name = row['Merchant Name'].strip()  # Strip to ensure matching whitespace is not an issue
        net_amount = row['Sum of Syn Net Amount']
        # If the merchant is found in the dictionary, we write its net amount to Excel
        if merchant_name in merchant_to_row:
            excel_row_num = merchant_to_row[merchant_name]
            cell_reference = f'{net_rtr_column}{excel_row_num}'
            worksheet[cell_reference].value = net_amount
        else:
            print(f"Merchant '{merchant_name}' not found in Excel sheet.")


# Function to process DataFrame and Excel data
def process_csv_and_excel(df_csv, workbook_bytes, sheet_name):
    # Open the Excel workbook from bytes
    workbook = openpyxl.load_workbook(filename=io.BytesIO(workbook_bytes))
    sheet = workbook[sheet_name]

    # Add Net RTR column if needed and get the letter of the Net RTR column
    net_rtr_column = add_net_rtr_column_if_needed(sheet)

    # Map 'Sum of Syn Net Amount' from DataFrame to Excel
    map_net_amount_to_excel(sheet, df_csv, net_rtr_column)

    # Save the workbook to a bytes object to return
    with io.BytesIO() as output_bytes:
        workbook.save(output_bytes)
        output_bytes.seek(0)
        workbook_bytes_updated = output_bytes.read()

    return workbook_bytes_updated

# Function to create log file for unmatched merchants
def create_log_for_unmatched(unmatched_merchants, log_file_path):
    with open(log_file_path, 'w') as file:
        for merchant, amount in unmatched_merchants.items():
            file.write(f'{merchant}: {amount}\n')


def add_data_to_sheet(workbook, df, sheet_name):
    sheet = workbook[sheet_name]
    print(f"Adding data to sheet '{sheet_name}'...")

    # Find duplicates in the Excel sheet
    duplicates = find_duplicates_in_column(sheet)
    print("Duplicates:", duplicates)

    # Extract merchant names from DataFrame
    df_merchants = set(df['Merchant Name'].dropna().unique())

    # Compare DataFrame merchants with worksheet merchants
    unmatched_merchants = df_merchants - set(str(m[0]).strip() for m in sheet.iter_rows(min_col=2, max_col=2, values_only=True) if m[0])


    print("Merchants not found in Excel sheet:", unmatched_merchants)

    # Optionally, log skipped entries
    skipped_entries = {"duplicates": duplicates, "unmatched": unmatched_merchants}
    log_skipped_entries(skipped_entries, sheet_name)

    # Ensure the Net RTR column is added and get its column letter
    net_rtr_column = add_net_rtr_column_if_needed(sheet)
    
    # Map 'Sum of Syn Net Amount' from DataFrame to Excel
    map_net_amount_to_excel(sheet, df, net_rtr_column)

    # Update the total Net RTR formula
    update_total_net_rtr_formula(sheet, net_rtr_column)

    # Save changes to the workbook directly if needed
    workbook.save("Backup.xlsx")


    output_bytes = BytesIO()
    workbook.save(output_bytes)
    output_bytes.seek(0)

    return output_bytes.getvalue()


def log_skipped_entries(skipped_entries, sheet_name):
    # Log or print skipped entries based on duplicates and unmatched merchants
    print(f"Skipped entries for '{sheet_name}':")
    for reason, merchants in skipped_entries.items():
        print(f"{reason.title()}: {', '.join(merchants)}")