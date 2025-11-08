# bluefolder_api/customers.py

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderCustomers(BlueFolderBase):
    """
    BlueFolder Customers API interface.

    Provides access to customer records and related data.  
    This domain allows you to:
      • Retrieve customer details by ID  
      • Search customers by name or other filters  
      • Retrieve locations associated with a given customer  

    Example
    -------
        >>> from bluefolder_api.client import BlueFolderClient
        >>> bf = BlueFolderClient()
        >>> customer = bf.customers.get_by_id(40296520)
        >>> print(customer['name'])
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderCustomers API handler.

        Parameters
        ----------
        client : BlueFolderClient, optional
            Shared client instance containing base_url, API key, and session.
        """
        super().__init__("customers", client=client)

    # -------------------------------------------------------------------------
    # CUSTOMER RETRIEVAL
    # -------------------------------------------------------------------------
    def get_by_id(self, customer_id: int):
        """
        Retrieve a single customer record by ID.

        Posts to:
            /api/2.0/customers/get.aspx

        Parameters
        ----------
        customer_id : int
            Numeric Customer ID.

        Returns
        -------
        dict
            Dictionary containing:
                - id, name, status
                - address, city, state, zip
                - phone, email, website
                - primaryContactId, notes
        """
        root = ET.Element("request")
        cust_get = ET.SubElement(root, "customerGet")
        ET.SubElement(cust_get, "id").text = str(customer_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("get", xml_data=xml_data)
        cust = xml_response.find(".//customer")
        if cust is None:
            return {}

        return {
            "id": cust.findtext("id"),
            "name": cust.findtext("name") or "",
            "status": cust.findtext("status") or "",
            "address": cust.findtext("addressStreet") or "",
            "city": cust.findtext("addressCity") or "",
            "state": cust.findtext("addressState") or "",
            "zip": cust.findtext("addressPostalCode") or "",
            "phone": cust.findtext("phone") or "",
            "email": cust.findtext("email") or "",
            "website": cust.findtext("website") or "",
            "primaryContactId": cust.findtext("primaryContactId"),
            "notes": cust.findtext("notes") or "",
        }

    # -------------------------------------------------------------------------
    def search_by_name(self, name: str):
        """
        Search for customers by (partial) name match.

        Posts to:
            /api/2.0/customers/list.aspx

        Parameters
        ----------
        name : str
            The customer name or substring to search for.

        Returns
        -------
        list[dict]
            List of matching customers with basic info.
        """
        root = ET.Element("request")
        cust_list = ET.SubElement(root, "customerList")
        ET.SubElement(cust_list, "name").text = name
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        customers = []
        for c in xml_response.findall(".//customer"):
            customers.append({
                "id": c.findtext("id"),
                "name": c.findtext("name") or "",
                "status": c.findtext("status") or "",
                "city": c.findtext("addressCity") or "",
                "state": c.findtext("addressState") or "",
            })
        return customers

    # -------------------------------------------------------------------------
    def get_location_by_id(self, location_id: int):
        """
        Retrieve a Customer Location record by ID.

        Posts to:
            /api/2.0/customers/getLocation.aspx

        Parameters
        ----------
        location_id : int
            Numeric Customer Location ID.

        Returns
        -------
        dict
            Dictionary containing location details, or empty dict if not found.
        """
        root = ET.Element("request")
        loc_get = ET.SubElement(root, "customerLocationGet")
        ET.SubElement(loc_get, "id").text = str(location_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("getLocation", xml_data=xml_data)
        loc = xml_response.find(".//customerLocation")
        if loc is None:
            return {}

        return {
            "id": loc.findtext("customerLocationId"),
            "customerId": loc.findtext("customerId"),
            "name": loc.findtext("locationName") or "",
            "address": loc.findtext("addressStreet") or "",
            "city": loc.findtext("addressCity") or "",
            "state": loc.findtext("addressState") or "",
            "zip": loc.findtext("addressPostalCode") or "",
            "notes": loc.findtext("locationNotes") or "",
        }
