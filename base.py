# bluefolder_api/base.py
import os
import requests

class BlueFolderClient:
    """Handles communication with the BlueFolder API."""
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("BLUEFOLDER_API_KEY")
        if not self.api_key:
            raise ValueError("BLUEFOLDER_API_KEY not set in environment or passed explicitly.")

        self.base_url = "https://app.bluefolder.com/api/2.0/"

    def request(self, method_name, params=None):
        payload = {
            "method": method_name,
            "apiKey": self.api_key,
        }
        if params:
            payload.update(params)

        response = requests.post(self.base_url, json=payload)
        response.raise_for_status()
        return response.json()
