import os
import requests
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union

# Load from .env if available
load_dotenv()

class BlueFolderBase(ABC):
    """
    Base class for all BlueFolder API modules.

    Handles:
    - API key management
    - Base URL validation
    - Payload construction
    - POST request dispatch
    - Basic error handling

    Extend this class in each module to reduce boilerplate and enforce consistency.
    """

    DEFAULT_BASE_URL = os.getenv("BLUEFOLDER_BASE_URL", "https://app.bluefolder.com/api/2.0/json/")

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        if not api_key or not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("A valid BlueFolder API key is required.")

        self.api_key = api_key.strip()
        self.base_url = base_url.strip() if base_url else self.DEFAULT_BASE_URL

        if not self.base_url.startswith("https://"):
            raise ValueError(f"Invalid base URL: {self.base_url}")

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _build_payload(self, payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        data = {"APIKEY": self.api_key}
        if payload:
            data.update(payload)
        return data

    def _build_url(self, endpoint: str) -> str:
        return os.path.join(self.base_url, endpoint)

    def _request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: int = 15,
    ) -> Union[Dict[str, Any], list]:
        """
        Performs a POST request to the BlueFolder API.
        Handles basic error parsing and raises exceptions on failure.
        """
        url = self._build_url(endpoint)
        data = self._build_payload(payload)

        try:
            response = requests.post(url, json=data, headers=self._headers(), timeout=timeout)
            response.raise_for_status()
            json_data = response.json()

            if "Error" in json_data:
                raise RuntimeError(f"BlueFolder API Error: {json_data['Error']}")

            return json_data
        except requests.RequestException as e:
            raise RuntimeError(f"BlueFolder API Request failed: {str(e)}") from e

    @abstractmethod
    def get_endpoint_name(self) -> str:
        """
        Returns the name of the endpoint module (e.g., 'Tasks', 'Users').
        Used for logging or CLI feedback. Must be implemented by subclasses.
        """
        pass
