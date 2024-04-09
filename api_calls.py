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
    
def download_excel_workbook(access_token, file_id):
    if access_token is None:
        print("Authentication required.")
        return None

    headers = {'Authorization': 'Bearer ' + access_token}
    endpoint = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content'
    response = requests.get(endpoint, headers=headers)

    response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    return response.content

    # print("Response:", response)

    # if response.status_code == 200:
    #     data = response.json()
    #     print("Workbook data:")
    #     print(data)
    #     return data

def update_workbook(access_token, file_id, workbook_bytes):
    if access_token is None:
        print("Authentication required.")
        return None

    headers = {'Authorization': 'Bearer ' + access_token}
    endpoint = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content'
    response = requests.put(endpoint, headers=headers, data=workbook_bytes)

    response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    return response.content
    