import xml.etree.ElementTree as ET
from datetime import date
from .base import BlueFolderBase 


class BlueFolderAppointments(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="appointments")

    def list_for_user_range(self, user_id: int, start_dt: str, end_dt: str):
        root = ET.Element("request")
        appt_list = ET.SubElement(root, "appointmentList")
        ET.SubElement(appt_list, "dateRangeStart").text = start_dt
        ET.SubElement(appt_list, "dateRangeEnd").text = end_dt
        ET.SubElement(appt_list, "userId").text = str(user_id)

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("list", xml_data=xml_data)

    def list_for_user_today(self, user_id: int):
        today = date.today().strftime("%Y-%m-%d")
        start = f"{today} 12:00 AM"
        end = f"{today} 11:59 PM"
        return self.list_for_user_range(user_id, start, end)

    def get_appointments_for_routing(self, user_id: int):
        xml = self.list_for_user_today(user_id)
        appointments = []
        for appt in xml.findall(".//appointment"):
            appointments.append({
                "id": appt.findtext("id"),
                "subject": appt.findtext("subject"),
                "start": appt.findtext("dateTimeStart"),
                "end": appt.findtext("dateTimeEnd"),
                "userId": appt.findtext(".//assignedTo/userId"),
            })
        return appointments
