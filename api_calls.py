import requests
from log import log_to_file

def get_excel_files(access_token):
    if access_token is None:
        print("Unable to fetch Excel Workbooks from Microsoft: Authentication required.")
        return []

    headers = {'Authorization': 'Bearer ' + access_token}
    endpoint = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        data = response.json()
        excel_files = [(item['name'], item['id']) for item in data['value'] if item['name'].endswith('.xlsx')]
        return excel_files
    else:
        print("Error fetching Excel Workbooks from Microsoft: {response.status_code} - {response.text}")
        return []
    
def download_excel_workbook(access_token, file_id, output_path, portfolio_name):
    if access_token is None:
        log_to_file("Unable to download Excel file from Microsoft: Authentication required.", output_path, portfolio_name)
        return None

    headers = {'Authorization': 'Bearer ' + access_token}
    endpoint = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content'
    response = requests.get(endpoint, headers=headers)

    response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    return response.content


# def update_workbook(access_token, file_id, workbook_bytes, output_path, portfolio_name):
#     if access_token is None:
#         log_to_file("Unable to update workbook to Microsoft: Authentication required.", output_path, portfolio_name)
#         return None
    

#     headers = {'Authorization': 'Bearer ' + access_token}
#     endpoint = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content'

#     workbook_bytes = b''.join(workbook_bytes)
    
#     response = requests.put(endpoint, headers=headers, data=workbook_bytes)

#     response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
#     return response.content

def update_workbook(access_token, file_id, workbook_bytes, output_path, portfolio_name):
    if access_token is None:
        log_to_file("Unable to update workbook to Microsoft: Authentication required.", output_path, portfolio_name)
        return None

    headers = {'Authorization': 'Bearer ' + access_token}
    endpoint = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content'

    if isinstance(workbook_bytes, bytes):
        data_to_send = workbook_bytes
    elif isinstance(workbook_bytes, list) and all(isinstance(item, bytes) for item in workbook_bytes):
        data_to_send = b''.join(workbook_bytes)
    else:
        log_to_file("Invalid type for workbook_bytes. Expected bytes or list of bytes.", output_path, portfolio_name)
        return None

    response = requests.put(endpoint, headers=headers, data=data_to_send)
    response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    return response.content
