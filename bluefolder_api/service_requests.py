import xml.etree.ElementTree as ET
from .base import BlueFolderBase

class BlueFolderServiceRequests(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="servicerequests")

    def list_for_user_range(self, user_id: int, start_date: str, end_date: str, date_range_type: str = "dateTimeCreated"):
        root = ET.Element("request")
        sr_list = ET.SubElement(root, "serviceRequestList")

        assigned_to = ET.SubElement(sr_list, "assignedTo")
        ET.SubElement(assigned_to, "userId").text = str(user_id)

        # Use dateRange wrapper with dateField attribute
        date_range = ET.SubElement(sr_list, "dateRange", {"dateField": date_range_type})
        ET.SubElement(date_range, "dateRangeStart").text = start_date
        ET.SubElement(date_range, "dateRangeEnd").text = end_date

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml = self._post("list", xml_data=xml_data)
        requests = []
        for sr in xml.findall(".//serviceRequest"):
            requests.append({
                "id": sr.findtext("id"),
                "subject": sr.findtext("subject"),
                "customerId": sr.findtext("customerId"),
                "address": sr.findtext("locationAddress"),
                "city": sr.findtext("locationCity"),
                "state": sr.findtext("locationState"),
                "zip": sr.findtext("locationZip"),
                "start": sr.findtext("dateTimeStart"),
                "end": sr.findtext("dateTimeEnd"),
                "userIds": [u.text for u in sr.findall(".//assignedTo/userId")]
            })
        return requests

    def list_for_range(self, start_date: str, end_date: str, date_field: str = "dateTimeCreated"):
        root = ET.Element("request")
        sr_list = ET.SubElement(root, "serviceRequestList")

        # Only date range for now (no assignedTo)
        date_range = ET.SubElement(sr_list, "dateRange", {"dateField": date_field})
        ET.SubElement(date_range, "dateRangeStart").text = start_date
        ET.SubElement(date_range, "dateRangeEnd").text = end_date

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml = self._post("list", xml_data=xml_data)
        requests = []
        for sr in xml.findall(".//serviceRequest"):
            requests.append({
                "id": sr.findtext("id"),
                "subject": sr.findtext("subject"),
                "customerId": sr.findtext("customerId"),
                "address": sr.findtext("locationAddress"),
                "city": sr.findtext("locationCity"),
                "state": sr.findtext("locationState"),
                "zip": sr.findtext("locationZip"),
                "start": sr.findtext("dateTimeStart"),
                "end": sr.findtext("dateTimeEnd"),
            })
        return requests
    
    def get_by_id(self, sr_id: int):
        """Retrieve a single Service Request by ID."""
        root = ET.Element("request")
        sr_get = ET.SubElement(root, "serviceRequestGet")
        ET.SubElement(sr_get, "serviceRequestId").text = str(sr_id) 
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        return self._post("get", xml_data=xml_data)