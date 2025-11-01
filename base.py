"""
Shared base class for all BlueFolder API domain clients.
Provides common functionality and error handling.
"""

from typing import Optional, Dict, Any, List
from .client import BlueFolderClient


class BlueFolderBase:
    """
    Abstract base class for BlueFolder API domain wrappers.
    Includes client initialization, input validation, and robust error handling.
    """

    def __init__(self, client: Optional[BlueFolderClient] = None) -> None:
        """
        Initialize with a shared BlueFolderClient instance.
        """
        self.client = client or BlueFolderClient()

    def validate_filters(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate filters passed to API requests.

        Args:
            filters (dict): Filter dictionary.

        Returns:
            dict: Validated filters.
        """
        if filters is None:
            return {}

        if not isinstance(filters, dict):
            raise TypeError(f"Filters must be a dict, got {type(filters)}")
        return filters

    def safe_get(self, endpoint: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform a safe GET request with validation and error catching.

        Args:
            endpoint (str): The BlueFolder API endpoint.
            filters (dict): Optional dictionary of query filters.

        Returns:
            list[dict]: API response data.
        """
        try:
            validated_filters = self.validate_filters(filters)
            response = self.client.get(endpoint, params=validated_filters)
            if not isinstance(response, list):
                raise ValueError(f"Expected list response, got {type(response)}")
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to fetch from '{endpoint}': {e}") from e
