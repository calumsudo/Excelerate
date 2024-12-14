import requests

class ApiService:
    BASE_URL = "https://graph.microsoft.com/v1.0/"

    @staticmethod
    def get_user_info(access_token):
        """Gets user info from Microsoft Graph API."""
        headers = {"Authorization": "Bearer " + access_token}
        response = requests.get(ApiService.BASE_URL + "me", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None