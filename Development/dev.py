import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import os

# Function to find duplicates in column B
def find_duplicates_in_column(worksheet, column='B'):
    values = {}
    duplicates = []
    for row in worksheet.iter_rows(min_col=2, max_col=2, values_only=True):
        merchant = row[0]
        if merchant in values:
            duplicates.append(merchant)
        values[merchant] = True
    return duplicates

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


# Function to map 'Sum of Syn Net Amount' from CSV to Excel
def map_net_amount_to_excel(worksheet, df_csv, net_rtr_column, header_row=2):
    # Convert the worksheet to a DataFrame for easier searching
    data = worksheet.values
    columns = next(data)[1:]
    df_excel = pd.DataFrame(data, columns=columns)

    # Find the index of the 'Merchant Name' column
    merchant_col_index = df_excel.columns.get_loc("Merchant Name") + 1  # +1 for 1-indexed column numbers in Excel

    # Iterate through the CSV DataFrame
    for index, row in df_csv.iterrows():
        merchant_name = row['Merchant Name']
        net_amount = row['Sum of Syn Net Amount']

        # Check if merchant exists in Excel
        if merchant_name in df_excel['Merchant Name'].values:
            # Get all row numbers for the merchant (in case there are duplicates)
            row_numbers = df_excel.index[df_excel['Merchant Name'] == merchant_name].tolist()
            
            # Loop through each row number and set the 'Net RTR' value
            for row_num in row_numbers:
                # Offset the row number to match the Excel file structure
                excel_row_num = row_num + header_row + 1
                # Set the value in the corresponding 'Net RTR' cell
                worksheet[f'{net_rtr_column}{excel_row_num}'].value = net_amount
        else:
            # Merchant not found, log or handle as needed
            pass


# Function to process CSV and Excel data
def process_csv_and_excel(csv_file_path, excel_file_path):
    # Load the CSV into a DataFrame
    df_csv = pd.read_csv(csv_file_path)

    # Open the Excel workbook
    wb = openpyxl.load_workbook(excel_file_path)
    sheet = wb['Kings']

    # Find duplicates in Excel sheet
    duplicates = find_duplicates_in_column(sheet)

    # Add Net RTR column if needed and get the letter of the Net RTR column
    net_rtr_column = add_net_rtr_column_if_needed(sheet)

    # Dictionary to hold unmatched merchant names
    unmatched_merchants = {}

    # Map 'Sum of Syn Net Amount' from CSV to Excel, skip duplicates and log unmatched names
    for index, row in df_csv.iterrows():
        merchant_name = row['Merchant Name']
        if merchant_name not in duplicates:
            # Find the row in Excel to add the value
            for row_excel in sheet.iter_rows(min_row=3, max_col=1, values_only=True):  # Assuming merchant names are in the first column
                if row_excel[0] == merchant_name:  # Adjust the index 0 if merchant names are in a different column
                    row_number = row_excel[0].row
                    cell_reference = f'{net_rtr_column}{row_number}'  # Construct the cell reference
                    sheet[cell_reference].value = row['Sum of Syn Net Amount']  # Set the value in the cell
                    break
            else:
                unmatched_merchants[merchant_name] = row['Sum of Syn Net Amount']
    
    # Save the Excel file
    wb.save(excel_file_path)

    # Return unmatched merchants
    return unmatched_merchants

# Function to create log file for unmatched merchants
def create_log_for_unmatched(unmatched_merchants, log_file_path):
    with open(log_file_path, 'w') as file:
        for merchant, amount in unmatched_merchants.items():
            file.write(f'{merchant}: {amount}\n')

# Main function call
if __name__ == "__main__":
    unmatched = process_csv_and_excel('kings.csv', 'Ass.xlsx')
    if unmatched:
        create_log_for_unmatched(unmatched, 'log.txt')


