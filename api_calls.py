import requests
from auth import global_access_token

def get_excel_files(access_token):
    if access_token is None:
        print("Authentication required.")
        return []

    headers = {'Authorization': 'Bearer ' + access_token}
    endpoint = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        data = response.json()
        excel_files = [(item['name'], item['id']) for item in data['value'] if item['name'].endswith('.xlsx')]
        print("Excel files:")
        print(excel_files)
        return excel_files
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []
    
def get_excel_workbook_sheets(access_token, workbook_name):
    if access_token is None:
        print("Authentication required.")
        return []

    headers = {'Authorization': 'Bearer ' + access_token}
    endpoint = f'https://graph.microsoft.com/v1.0/me/drive/root:/{workbook_name}:/workbook/worksheets'
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        data = response.json()
        sheets = [item['name'] for item in data['value']]
        return sheets
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []