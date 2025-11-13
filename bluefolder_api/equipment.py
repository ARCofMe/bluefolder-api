"""BlueFolder equipment domain helpers."""

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderEquipment(BlueFolderBase):
    """
    BlueFolder Equipment API interface.

    Provides access to equipment records, including asset tracking,
    model/serial information, and maintenance relationships.

    Common uses:
      • Retrieve equipment for a specific customer or location
      • Track equipment by serial or model number
      • Enrich Service Requests with associated assets
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderEquipment API handler.
        """
        super().__init__("equipment", client=client)

    # -------------------------------------------------------------------------
    def get_by_id(self, equipment_id: int):
        """
        Retrieve an equipment record by its ID.

        Parameters
        ----------
        equipment_id : int
            Numeric Equipment ID.

        Returns
        -------
        dict
            Equipment details or empty dict if not found.
        """
        root = ET.Element("request")
        eq_get = ET.SubElement(root, "equipmentGet")
        ET.SubElement(eq_get, "id").text = str(equipment_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("get", xml_data=xml_data)
        eq = xml_response.find(".//equipment")
        if eq is None:
            return {}

        return {
            "id": eq.findtext("id"),
            "name": eq.findtext("name"),
            "model": eq.findtext("model"),
            "serialNumber": eq.findtext("serialNumber"),
            "manufacturer": eq.findtext("manufacturer"),
            "customerId": eq.findtext("customerId"),
            "locationId": eq.findtext("customerLocationId"),
            "installDate": eq.findtext("installDate"),
            "warrantyEndDate": eq.findtext("warrantyEndDate"),
            "notes": eq.findtext("notes"),
        }

    # -------------------------------------------------------------------------
    def list_for_customer(self, customer_id: int):
        """
        Retrieve all equipment belonging to a given customer.

        Parameters
        ----------
        customer_id : int
            Numeric Customer ID.

        Returns
        -------
        list[dict]
            List of equipment records.
        """
        root = ET.Element("request")
        eq_list = ET.SubElement(root, "equipmentList")
        ET.SubElement(eq_list, "customerId").text = str(customer_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        equipment = []
        for eq in xml_response.findall(".//equipment"):
            equipment.append(
                {
                    "id": eq.findtext("id"),
                    "name": eq.findtext("name"),
                    "model": eq.findtext("model"),
                    "serialNumber": eq.findtext("serialNumber"),
                    "locationId": eq.findtext("customerLocationId"),
                    "installDate": eq.findtext("installDate"),
                }
            )
        return equipment
