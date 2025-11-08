# bluefolder_api/tax_codes.py

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderTaxCodes(BlueFolderBase):
    """
    BlueFolder Tax Codes API interface.

    Provides access to tax code definitions used for billing
    on materials, labor, and service requests.
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderTaxCodes API handler.
        """
        super().__init__("taxCodes", client=client)

    # -------------------------------------------------------------------------
    def list_all(self):
        """
        Retrieve all defined tax codes.

        Returns
        -------
        list[dict]
            List of tax code details.
        """
        xml_response = self._post("list")
        tax_codes = []
        for t in xml_response.findall(".//taxCode"):
            tax_codes.append({
                "id": t.findtext("id"),
                "name": t.findtext("name"),
                "rate": t.findtext("rate"),
                "isDefault": t.findtext("isDefault") == "1",
                "description": t.findtext("description") or "",
            })
        return tax_codes
