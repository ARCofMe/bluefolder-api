# bluefolder_api/materials.py

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderMaterials(BlueFolderBase):
    """
    BlueFolder Materials API interface.

    Manages material items (inventory, billable parts, consumables)
    associated with Service Requests or inventory tracking.
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderMaterials API handler.
        """
        super().__init__("materials", client=client)

    # -------------------------------------------------------------------------
    def list_for_service_request(self, service_request_id: int):
        """
        Retrieve materials associated with a specific Service Request.

        Parameters
        ----------
        service_request_id : int
            Numeric Service Request ID.

        Returns
        -------
        list[dict]
            List of material entries.
        """
        root = ET.Element("request")
        mat_list = ET.SubElement(root, "materialList")
        ET.SubElement(mat_list, "serviceRequestId").text = str(service_request_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        materials = []
        for m in xml_response.findall(".//material"):
            materials.append({
                "id": m.findtext("id"),
                "itemName": m.findtext("itemName"),
                "description": m.findtext("description"),
                "quantity": m.findtext("quantity"),
                "unitPrice": m.findtext("unitPrice"),
                "total": m.findtext("total"),
                "isBillable": m.findtext("isBillable") == "1",
            })
        return materials

    # -------------------------------------------------------------------------
    def add_to_service_request(self, service_request_id: int, item_name: str, quantity: float, unit_price: float, description: str = "", is_billable: bool = True):
        """
        Add a material item to a Service Request.

        Parameters
        ----------
        service_request_id : int
            Service Request ID.
        item_name : str
            Name of the item/material.
        quantity : float
            Quantity used.
        unit_price : float
            Price per unit.
        description : str, optional
            Description of the item.
        is_billable : bool, default True
            Whether the material is billable to the customer.

        Returns
        -------
        xml.etree.ElementTree.Element
            Raw XML response from BlueFolder.
        """
        root = ET.Element("request")
        mat_add = ET.SubElement(root, "materialAdd")
        ET.SubElement(mat_add, "serviceRequestId").text = str(service_request_id)
        ET.SubElement(mat_add, "itemName").text = item_name
        ET.SubElement(mat_add, "description").text = description
        ET.SubElement(mat_add, "quantity").text = str(quantity)
        ET.SubElement(mat_add, "unitPrice").text = str(unit_price)
        ET.SubElement(mat_add, "isBillable").text = "1" if is_billable else "0"
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        return self._post("add", xml_data=xml_data)
