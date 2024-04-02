from openpyxl import load_workbook
import io
import os
from datetime import datetime

def get_workbook_data(workbook_bytes, selected_file):

    workbook = load_workbook(filename=io.BytesIO(workbook_bytes))

    # Save a copy of the workbook to local machine
    current_date = datetime.now()
    date_string = current_date.strftime("%Y_%m_%d")
    file_path_backup = os.path.expanduser(f"~/Desktop/Excelerator/{selected_file}_BACKUP{date_string}.xlsx")

    with open(file_path_backup, "wb") as file:
        file.write(workbook_bytes)

    # Get all sheet names
    for sheet in workbook.sheetnames:
        print(sheet)

    return workbook




def add_data_to_kings_sheet(workbook, pivot_table):
    # Get the 'Kings' sheet
    kings_sheet = workbook['Kings']

    print("Adding data to Kings sheet...")
    print("Pivot Table:", pivot_table)

    for row in kings_sheet.iter_rows(min_row=1, max_row=3, values_only=True):
        print(row)


    return workbook
