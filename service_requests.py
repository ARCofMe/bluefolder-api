"""
Module for interacting with the BlueFolder Service Requests API.
Provides functionality to retrieve service requests from the BlueFolder API.
"""

from .base import BlueFolderBase


class BlueFolderServiceRequests(BlueFolderBase):
    """Handles Service Request-related interactions with the BlueFolder API."""

    def get(self, filters: dict = None) -> list[dict]:
        """
        Retrieve service requests from the BlueFolder API.

        Args:
            filters (dict, optional): A dictionary of filter parameters for the request.

        Returns:
            list[dict]: A list of service requests.
        """
        return self.client.get("servicerequests", params=filters or {})
