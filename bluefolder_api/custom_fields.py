"""Expose BlueFolder custom field metadata via Python."""

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderCustomFields(BlueFolderBase):
    """
    BlueFolder Custom Fields API interface.

    Provides methods to retrieve, list, or inspect custom fields that exist
    across entities (Customers, Service Requests, Equipment, etc.).
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderCustomFields API handler.

        Parameters
        ----------
        client : BlueFolderClient, optional
            Shared client instance containing base_url, API key, and session.
        """
        super().__init__("customFields", client=client)

    # -------------------------------------------------------------------------
    def list_all(self):
        """
        Retrieve all defined custom fields in the system.

        Posts to:
            /api/2.0/customFields/list.aspx

        Returns
        -------
        list[dict]
            List of custom field metadata (id, name, type, and entity type).
        """
        xml_response = self._post("list")

        fields = []
        for f in xml_response.findall(".//customField"):
            fields.append(
                {
                    "id": f.findtext("id"),
                    "name": f.findtext("name"),
                    "entityType": f.findtext("entityType"),
                    "dataType": f.findtext("dataType"),
                    "isRequired": f.findtext("isRequired") == "1",
                }
            )
        return fields
