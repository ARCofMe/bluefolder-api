"""Customer contact endpoints for the BlueFolder API."""

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderCustomerContacts(BlueFolderBase):
    """
    BlueFolder Customer Contacts API interface.

    Provides access to customer contact records, including phone, email,
    role, and location relationships.
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderCustomerContacts API handler.
        """
        super().__init__("customerContacts", client=client)

    # -------------------------------------------------------------------------
    def list_for_customer(self, customer_id: int):
        """
        Retrieve all contacts associated with a specific customer.

        Parameters
        ----------
        customer_id : int
            Numeric Customer ID.

        Returns
        -------
        list[dict]
            List of customer contacts.
        """
        root = ET.Element("request")
        contact_list = ET.SubElement(root, "customerContactList")
        ET.SubElement(contact_list, "customerId").text = str(customer_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        contacts = []
        for c in xml_response.findall(".//customerContact"):
            contacts.append(
                {
                    "id": c.findtext("id"),
                    "firstName": c.findtext("firstName"),
                    "lastName": c.findtext("lastName"),
                    "title": c.findtext("title"),
                    "email": c.findtext("email"),
                    "phone": c.findtext("phone"),
                    "isPrimary": c.findtext("isPrimary") == "1",
                    "locationId": c.findtext("customerLocationId"),
                }
            )
        return contacts

    # -------------------------------------------------------------------------
    def get_by_id(self, contact_id: int):
        """
        Retrieve a specific customer contact by ID.

        Parameters
        ----------
        contact_id : int
            Numeric Contact ID.

        Returns
        -------
        dict
            Contact details dictionary, or empty if not found.
        """
        root = ET.Element("request")
        contact_get = ET.SubElement(root, "customerContactGet")
        ET.SubElement(contact_get, "id").text = str(contact_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("get", xml_data=xml_data)
        c = xml_response.find(".//customerContact")
        if c is None:
            return {}

        return {
            "id": c.findtext("id"),
            "firstName": c.findtext("firstName"),
            "lastName": c.findtext("lastName"),
            "title": c.findtext("title"),
            "email": c.findtext("email"),
            "phone": c.findtext("phone"),
            "isPrimary": c.findtext("isPrimary") == "1",
            "locationId": c.findtext("customerLocationId"),
        }
