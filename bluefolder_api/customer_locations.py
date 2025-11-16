"""Utilities for resolving customer locations via the BlueFolder API."""

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderCustomerLocations(BlueFolderBase):
    """
    BlueFolder Customer Locations API interface.

    Provides access to customer location data (addresses, zones, and service metadata).
    This domain allows retrieval of all locations for a given customer, fetching specific
    locations by ID, and identifying a customer's primary service address.

    Common use cases:
      • Resolve addresses for routing and mapping
      • Fetch assigned technicians or managers for a site
      • Enrich Service Request or Assignment records with location data

    Example
    -------
        >>> from bluefolder_api.client import BlueFolderClient
        >>> bf = BlueFolderClient()
        >>> locations = bf.customer_locations.get_by_customer_id(12345)
        >>> print(locations[0]['address'])
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderCustomerLocations API handler.

        Parameters
        ----------
        client : BlueFolderClient, optional
            Shared client instance containing base_url, API key, and session.
        """
        super().__init__("customer", client=client)

    # -------------------------------------------------------------------------
    # LOCATION LISTING
    # -------------------------------------------------------------------------
    def get_by_customer_id(self, customer_id: int):
        """
        Retrieve all locations associated with a specific customer.

        Constructs and posts an XML request to:
            /api/2.0/customer/list.aspx

        Parameters
        ----------
        customer_id : int
            The numeric Customer ID whose locations should be retrieved.

        Returns
        -------
        list[dict]
            A list of customer location dictionaries containing:
                - id (str)
                - customerId (str)
                - name (str)
                - isPrimary (bool)
                - address, city, state, zip
                - notes, zone
                - serviceManagerId, technicianId
        """
        root = ET.Element("request")
        loc_list = ET.SubElement(root, "customerLocationList")
        ET.SubElement(loc_list, "customerId").text = str(customer_id)

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        xml_response = self._post("list", xml_data=xml_data)

        locations = []
        for loc in xml_response.findall(".//customerLocation"):
            locations.append(
                {
                    "id": loc.findtext("customerLocationId"),
                    "customerId": loc.findtext("customerId"),
                    "name": loc.findtext("locationName") or "",
                    "isPrimary": loc.findtext("isPrimary") == "1",
                    "address": loc.findtext("addressStreet") or "",
                    "city": loc.findtext("addressCity") or "",
                    "state": loc.findtext("addressState") or "",
                    "zip": loc.findtext("addressPostalCode") or "",
                    "notes": loc.findtext("locationNotes") or "",
                    "zone": loc.findtext("zone") or "",
                    "serviceManagerId": loc.findtext("serviceManagerId"),
                    "technicianId": loc.findtext("technicianId"),
                }
            )
        return locations

    # -------------------------------------------------------------------------
    def get_location(self, location_id: int):
        """
        Retrieve a single customer location by ID.

        Constructs and posts an XML request to:
            /api/2.0/customer/getLocation.aspx

        Parameters
        ----------
        location_id : int
            The numeric Customer Location ID.

        Returns
        -------
        dict
            Dictionary containing location details (address, city, state, zip, etc.)
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
            "isPrimary": loc.findtext("isPrimary") == "1",
            "address": loc.findtext("addressStreet") or "",
            "city": loc.findtext("addressCity") or "",
            "state": loc.findtext("addressState") or "",
            "zip": loc.findtext("addressPostalCode") or "",
            "notes": loc.findtext("locationNotes") or "",
            "zone": loc.findtext("zone") or "",
            "serviceManagerId": loc.findtext("serviceManagerId"),
            "technicianId": loc.findtext("technicianId"),
        }

    # -------------------------------------------------------------------------
    def get_primary_for_customer(self, customer_id: int):
        """
        Retrieve the primary location for a given customer (if defined).

        Parameters
        ----------
        customer_id : int
            The numeric Customer ID.

        Returns
        -------
        dict | None
            Dictionary of the primary location, or None if not found.
        """
        locations = self.get_by_customer_id(customer_id)
        for loc in locations:
            if loc.get("isPrimary"):
                return loc
        return locations[0] if locations else None

    # -------------------------------------------------------------------------
    # CREATE / UPDATE / DELETE
    # -------------------------------------------------------------------------
    def add(self, customer_id: int, **fields):
        """Add a location to a customer."""
        root = ET.Element("request")
        loc_add = ET.SubElement(root, "customerLocationAdd")
        ET.SubElement(loc_add, "customerId").text = str(customer_id)
        for key, val in fields.items():
            if val is None:
                continue
            ET.SubElement(loc_add, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("addLocation", xml_data=xml_data, override_url=f"{self.base_url}/customers/addLocation.aspx")

    def edit(self, location_id: int, **fields):
        """Edit an existing location."""
        root = ET.Element("request")
        loc_edit = ET.SubElement(root, "customerLocationEdit")
        ET.SubElement(loc_edit, "customerLocationId").text = str(location_id)
        for key, val in fields.items():
            if val is None:
                continue
            ET.SubElement(loc_edit, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("editLocation", xml_data=xml_data, override_url=f"{self.base_url}/customers/editLocation.aspx")

    def delete(self, location_id: int):
        """Delete a location."""
        root = ET.Element("request")
        loc_del = ET.SubElement(root, "customerLocationDelete")
        ET.SubElement(loc_del, "customerLocationId").text = str(location_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("deleteLocation", xml_data=xml_data, override_url=f"{self.base_url}/customers/deleteLocation.aspx")
