import msal
import requests

# Define your constants
APPLICATION_ID = 'c5b98c30-7848-4882-8e16-77cb80812d55'
AUTHORITY_URL = 'https://login.microsoftonline.com/consumers/'
SCOPES = ['User.Read', 'Files.ReadWrite.All']
base_url = 'https://graph.microsoft.com/v1.0/'

def initiate_device_flow():
    app = msal.PublicClientApplication(APPLICATION_ID, authority=AUTHORITY_URL)
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise Exception("Failed to create device flow")
    return flow

def authenticate(flow):
    print("Checking for authentication...")
    app = msal.PublicClientApplication(APPLICATION_ID, authority=AUTHORITY_URL)

    result = app.acquire_token_by_device_flow(flow)
    print("RESULT: ", result)

    access_token_id = result['access_token']
    headers = {'Authorization': 'Bearer ' + access_token_id}

    endpoint = base_url + 'me'
    response = requests.get(endpoint, headers=headers)
    print("RESPONSE: ", response)
    print("RESPONSE JSON: ", response.json())

    # try:
    #     # This call blocks until the user completes the login process or an error occurs
    #     result = app.acquire_token_by_device_flow(flow)
    #     print("RESULT: ")
    #     print(result.get("access_token"))
    #     if "access_token" in result:
    #         return True, result['access_token']  # Authentication successful
    #     else:
    #         print("Authentication failed or was cancelled by the user.")
    #         return False, None
    # except Exception as e:
    #     print(f"An error occurred during authentication: {e}")
    #     return False, None
