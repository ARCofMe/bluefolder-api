import xml.etree.ElementTree as ET
from .base import BlueFolderBase

class BlueFolderCustomers(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="customers")

    def get_location_by_id(self, location_id: int):
        """Retrieve Customer Location by ID."""
        root = ET.Element("request")
        loc_get = ET.SubElement(root, "customerLocationGet")
        ET.SubElement(loc_get, "customerLocationId").text = str(location_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        return self._post("getLocation", xml_data=xml_data)
