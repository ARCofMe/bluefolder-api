"""Customer contact endpoints for the BlueFolder API."""

import logging
import xml.etree.ElementTree as ET
from .base import BlueFolderBase

logger = logging.getLogger(__name__)


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
        try:
            if self.client and hasattr(self.client, "customers"):
                xml_response = self.client.customers.get_by_id(customer_id)
            else:
                xml_response = self._customer_get_fallback(customer_id)
        except Exception as exc:
            if self._is_optional_endpoint_error(exc):
                logger.warning("Customer contact lookup unavailable for this tenant: %s", exc)
                return []
            raise
        contacts = []
        for c in xml_response.findall(".//customerContact"):
            contacts.append(
                {
                    "id": c.findtext("customerContactId") or c.findtext("id"),
                    "customerId": c.findtext("customerId"),
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
        ET.SubElement(contact_get, "customerContactId").text = str(contact_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        try:
            xml_response = self._post(
                "getContact",
                xml_data=xml_data,
                override_url=f"{self.base_url}/customers/getContact.aspx",
            )
        except Exception as exc:
            if self._is_optional_endpoint_error(exc):
                logger.warning("Customer contacts get endpoint unavailable for this tenant: %s", exc)
                return {}
            raise
        c = xml_response.find(".//customerContact")
        if c is None:
            return {}

        return {
            "id": c.findtext("customerContactId") or c.findtext("id"),
            "customerId": c.findtext("customerId"),
            "firstName": c.findtext("firstName"),
            "lastName": c.findtext("lastName"),
            "title": c.findtext("title"),
            "email": c.findtext("email"),
            "phone": c.findtext("phone"),
            "isPrimary": c.findtext("isPrimary") == "1",
            "locationId": c.findtext("customerLocationId"),
        }

    # -------------------------------------------------------------------------
    def add(self, customer_id: int, **fields):
        """Add a contact to a customer."""
        root = ET.Element("request")
        contact_add = ET.SubElement(root, "customerContactAdd")
        ET.SubElement(contact_add, "customerId").text = str(customer_id)
        for key, val in fields.items():
            if val is None:
                continue
            ET.SubElement(contact_add, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post(
            "addContact",
            xml_data=xml_data,
            override_url=f"{self.base_url}/customers/addContact.aspx",
        )

    def edit(self, contact_id: int, **fields):
        """Edit an existing contact."""
        root = ET.Element("request")
        contact_edit = ET.SubElement(root, "customerContactEdit")
        ET.SubElement(contact_edit, "customerContactId").text = str(contact_id)
        for key, val in fields.items():
            if val is None:
                continue
            ET.SubElement(contact_edit, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post(
            "editContact",
            xml_data=xml_data,
            override_url=f"{self.base_url}/customers/editContact.aspx",
        )

    def delete(self, contact_id: int):
        """Delete a contact."""
        root = ET.Element("request")
        contact_del = ET.SubElement(root, "customerContactDelete")
        ET.SubElement(contact_del, "id").text = str(contact_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post(
            "deleteContact",
            xml_data=xml_data,
            override_url=f"{self.base_url}/customers/deleteContact.aspx",
        )

    @staticmethod
    def _is_optional_endpoint_error(exc: Exception) -> bool:
        """Return whether a tenant appears not to support the customerContacts read endpoints."""
        message = str(exc).lower()
        return "404" in message or "resource cannot be found" in message or "not found" in message

    def _customer_get_fallback(self, customer_id: int):
        """Fallback to the documented customers/get.aspx payload when no shared client is available."""
        root = ET.Element("request")
        ET.SubElement(root, "customerId").text = str(customer_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post(
            "get",
            xml_data=xml_data,
            override_url=f"{self.base_url}/customers/get.aspx",
        )
