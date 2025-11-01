import os
import requests
from typing import Optional, Dict, Any


class BlueFolderBase:
    """
    Base class to handle HTTP interactions with the BlueFolder API.
    """

    def __init__(self, api_key: str, base_url: str = "https://app.bluefolder.com/api/2.0/json/"):
        if not api_key:
            raise ValueError("API key is required.")
        self.api_key = api_key
        self.base_url = base_url

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Any:
        url = os.path.join(self.base_url, endpoint)
        if not url.startswith("https://"):
            raise ValueError(f"Invalid URL: {url}")

        data = {
            "APIKEY": self.api_key
        }
        if payload:
            data.update(payload)

        try:
            response = requests.post(url, json=data, headers=self._headers(), timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"API request to {url} failed: {e}") from e

        result = response.json()
        if "Error" in result:
            raise RuntimeError(f"API Error: {result['Error']}")

        return result
