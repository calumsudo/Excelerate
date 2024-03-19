import msal
import requests
import webbrowser
import threading
import pyperclip

# Define your constants
APPLICATION_ID = 'c5b98c30-7848-4882-8e16-77cb80812d55'
AUTHORITY_URL = 'https://login.microsoftonline.com/consumers/'
SCOPES = ['User.Read', 'Files.ReadWrite.All']
base_url = 'https://graph.microsoft.com/v1.0/'
global_access_token = None

def initiate_device_flow():
    app = msal.PublicClientApplication(APPLICATION_ID, authority=AUTHORITY_URL)
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise Exception("Failed to create device flow")
    
    # Open the verification URL in the user's web browser
    webbrowser.open(flow['verification_uri'])
    print("User code: ", flow['user_code'])
    pyperclip.copy(flow['user_code'])
    
    return flow

def authenticate(flow, callback):
    def run_authentication():
        print("Checking for authentication...")
        app = msal.PublicClientApplication(APPLICATION_ID, authority=AUTHORITY_URL)
        result = app.acquire_token_by_device_flow(flow)
        print("RESULT: ", result)

        if "access_token" in result:
            access_token = result['access_token']
            headers = {'Authorization': 'Bearer ' + access_token}
            endpoint = base_url + 'me'
            response = requests.get(endpoint, headers=headers)
            print("RESPONSE: ", response)
            print("RESPONSE JSON: ", response.json())
            callback(True, response.json(), access_token)  # Pass the access_token to the callback
        else:
            callback(False, None, None)  # Indicate failure

    # Start the authentication process in a background thread
    threading.Thread(target=run_authentication).start()
