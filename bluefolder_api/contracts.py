# bluefolder_api/contracts.py

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderContracts(BlueFolderBase):
    """
    BlueFolder Contracts API interface.

    Provides access to customer contract details, such as service level,
    expiration dates, and coverage limits.
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderContracts API handler.
        """
        super().__init__("contracts", client=client)

    # -------------------------------------------------------------------------
    def list_for_customer(self, customer_id: int):
        """
        Retrieve all contracts associated with a given customer.

        Parameters
        ----------
        customer_id : int
            Numeric Customer ID.

        Returns
        -------
        list[dict]
            List of contract details.
        """
        root = ET.Element("request")
        contract_list = ET.SubElement(root, "contractList")
        ET.SubElement(contract_list, "customerId").text = str(customer_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        contracts = []
        for c in xml_response.findall(".//contract"):
            contracts.append({
                "id": c.findtext("id"),
                "name": c.findtext("name"),
                "number": c.findtext("number"),
                "startDate": c.findtext("startDate"),
                "endDate": c.findtext("endDate"),
                "status": c.findtext("status"),
                "coverage": c.findtext("coverageDescription"),
            })
        return contracts
