"""
Encapsulates low-level HTTP logic for BlueFolder API.
Handles authentication, retries, and standardized error handling.
"""

import os
import time
import logging
import requests
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)


class BlueFolderClient:
    """
    A reusable, low-level client for communicating with the BlueFolder API.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://app.bluefolder.com/api/3.0/"):
        """
        Initializes the client with an API key and optional custom base URL.

        Args:
            api_key (str): Your BlueFolder API key. If not passed, it is read from the BLUEFOLDER_API_KEY env variable.
            base_url (str): The base URL for BlueFolder’s API.
        """
        self.api_key = api_key or os.getenv("BLUEFOLDER_API_KEY")
        if not self.api_key:
            raise ValueError("Missing BlueFolder API key. Set BLUEFOLDER_API_KEY or pass one in.")

        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, retries: int = 3, backoff: float = 1.0) -> Union[Dict, list]:
        """
        Perform a GET request to the BlueFolder API with retry logic.

        Args:
            endpoint (str): API endpoint path (e.g., "users", "appointments").
            params (dict): Optional query parameters.
            retries (int): Number of retries on failure.
            backoff (float): Delay in seconds between retries.

        Returns:
            Union[dict, list]: Parsed JSON response.

        Raises:
            RuntimeError: If the request fails after retries.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        attempt = 0

        while attempt < retries:
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                attempt += 1
                logger.warning(f"GET attempt {attempt} failed for {url}: {e}")
                if attempt >= retries:
                    raise RuntimeError(f"GET request to {url} failed after {retries} attempts.") from e
                time.sleep(backoff)

    def post(self, endpoint: str, data: Dict[str, Any], retries: int = 3, backoff: float = 1.0) -> Dict[str, Any]:
        """
        Perform a POST request to the BlueFolder API with retry logic.

        Args:
            endpoint (str): API endpoint path.
            data (dict): Payload to send.
            retries (int): Number of retries on failure.
            backoff (float): Delay in seconds between retries.

        Returns:
            dict: Parsed JSON response.

        Raises:
            RuntimeError: If the request fails after retries.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        attempt = 0

        while attempt < retries:
            try:
                response = self.session.post(url, json=data, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                attempt += 1
                logger.warning(f"POST attempt {attempt} failed for {url}: {e}")
                if attempt >= retries:
                    raise RuntimeError(f"POST request to {url} failed after {retries} attempts.") from e
                time.sleep(backoff)
