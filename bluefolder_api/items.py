"""Items API wrapper for BlueFolder price list/catalog items."""

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderItems(BlueFolderBase):
    """Wraps /items endpoints (add/edit/delete/get/list)."""

    def __init__(self, client=None):
        super().__init__("items", client=client)

    def list(self, **filters):
        """List items with optional filters (e.g., itemListId)."""
        root = ET.Element("request")
        item_list = ET.SubElement(root, "itemList")
        for key, val in filters.items():
            if val is None:
                continue
            ET.SubElement(item_list, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("list", xml_data=xml_data)

    def get(self, item_id: int):
        """Get a single item by ID."""
        root = ET.Element("request")
        item_get = ET.SubElement(root, "itemGet")
        ET.SubElement(item_get, "itemId").text = str(item_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("get", xml_data=xml_data)

    def add(self, **fields):
        """Add a new item."""
        root = ET.Element("request")
        item_add = ET.SubElement(root, "itemAdd")
        for key, val in fields.items():
            if val is None:
                continue
            ET.SubElement(item_add, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("add", xml_data=xml_data)

    def edit(self, item_id: int, **fields):
        """Edit an existing item."""
        root = ET.Element("request")
        item_edit = ET.SubElement(root, "itemEdit")
        ET.SubElement(item_edit, "itemId").text = str(item_id)
        for key, val in fields.items():
            if val is None:
                continue
            ET.SubElement(item_edit, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("edit", xml_data=xml_data)

    def delete(self, item_id: int):
        """Delete an item by ID."""
        root = ET.Element("request")
        item_del = ET.SubElement(root, "itemDelete")
        ET.SubElement(item_del, "itemId").text = str(item_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("delete", xml_data=xml_data)
