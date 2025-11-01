"""
Module for interacting with the BlueFolder Materials API.
Provides functionality to retrieve materials from the BlueFolder API.
"""

from .base import BlueFolderBase


class BlueFolderMaterials(BlueFolderBase):
    """Handles Material-related interactions with the BlueFolder API."""

    def get(self, filters: dict = None) -> list[dict]:
        """
        Retrieve materials from the BlueFolder API.

        Args:
            filters (dict, optional): A dictionary of filter parameters for the request.

        Returns:
            list[dict]: A list of materials.
        """
        return self.client.get("materials", params=filters or {})
