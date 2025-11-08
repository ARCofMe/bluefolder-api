import xml.etree.ElementTree as ET
from .base import BlueFolderBase

class BlueFolderCustomerLocations(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="customer")

    def get_by_customer_id(self, customer_id: int):
        root = ET.Element("request")
        loc_list = ET.SubElement(root, "customerLocationList")
        ET.SubElement(loc_list, "customerId").text = str(customer_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml = self._post("list", xml_data=xml_data)
        locations = []
        for loc in xml.findall(".//customerLocation"):
            locations.append({
                "id": loc.findtext("customerLocationId"),
                "name": loc.findtext("locationName") or "",
                "isPrimary": loc.findtext("isPrimary") or False,
                "customerId": loc.findtext("customerId"),
                "name": loc.findtext("locationName") or "",
                "address": loc.findtext("addressStreet") or "",
                "city": loc.findtext("addressCity") or "",
                "state": loc.findtext("addressState") or "",
                "zip": loc.findtext("addressPostalCode") or "",
                "notes": loc.findtext("locationNotes") or "",
                "zone": loc.findtext("zone") or "",
                "serviceManagerId": loc.findtext("serviceManagerId"),
                "technicianId": loc.findtext("technicianId")
            })
        return locations
