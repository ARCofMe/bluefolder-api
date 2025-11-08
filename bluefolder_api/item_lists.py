# bluefolder_api/item_lists.py

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderItemLists(BlueFolderBase):
    """
    BlueFolder Item Lists API interface.

    Provides access to predefined item lists (price books, parts catalogs)
    used for selecting materials or services.
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderItemLists API handler.
        """
        super().__init__("itemLists", client=client)

    # -------------------------------------------------------------------------
    def list_all(self):
        """
        Retrieve all item lists.

        Returns
        -------
        list[dict]
            List of item list summaries.
        """
        xml_response = self._post("list")
        item_lists = []
        for i in xml_response.findall(".//itemList"):
            item_lists.append({
                "id": i.findtext("id"),
                "name": i.findtext("name"),
                "type": i.findtext("listType"),
                "dateCreated": i.findtext("dateCreated"),
            })
        return item_lists

    # -------------------------------------------------------------------------
    def get_items(self, list_id: int):
        """
        Retrieve individual items within a given Item List.

        Parameters
        ----------
        list_id : int
            Numeric Item List ID.

        Returns
        -------
        list[dict]
            List of items in the list.
        """
        root = ET.Element("request")
        item_list_get = ET.SubElement(root, "itemListGet")
        ET.SubElement(item_list_get, "id").text = str(list_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("get", xml_data=xml_data)
        items = []
        for item in xml_response.findall(".//item"):
            items.append({
                "id": item.findtext("id"),
                "name": item.findtext("name"),
                "description": item.findtext("description"),
                "price": item.findtext("unitPrice"),
                "sku": item.findtext("sku"),
                "category": item.findtext("category"),
            })
        return items
