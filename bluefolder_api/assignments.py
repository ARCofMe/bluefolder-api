import xml.etree.ElementTree as ET
from .base import BlueFolderBase
from datetime import date

class BlueFolderAssignments(BlueFolderBase):
    def __init__(self):
        # Note: The domain here is still "serviceRequests"
        # because the endpoint is nested under that path.
        super().__init__(domain="serviceRequests")

    def list_for_user_range(
        self,
        user_id: int,
        start_date: str,
        end_date: str,
        date_range_type: str = "scheduled",
    ):
        """
        Retrieve a list of service request assignments for a user within a date range.
        """
        root = ET.Element("request")
        sr_assign_list = ET.SubElement(root, "serviceRequestAssignmentList")

        # Core filters
        ET.SubElement(sr_assign_list, "dateRangeStart").text = start_date
        ET.SubElement(sr_assign_list, "dateRangeEnd").text = end_date
        ET.SubElement(sr_assign_list, "dateRangeType").text = date_range_type

        # Assigned user filter
        assigned_to = ET.SubElement(sr_assign_list, "assignedTo")
        ET.SubElement(assigned_to, "userId").text = str(user_id)

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        # Note: Explicit override of path since endpoint doesn’t match domain pattern
        url_override = f"{self.base_url.rsplit('/', 1)[0]}/serviceRequests/getAssignmentList.aspx"
        xml = self._post("getAssignmentList", xml_data=xml_data, override_url=url_override)

        assignments = []
        for a in xml.findall(".//serviceRequestAssignment"):
            assignments.append({
                "assignmentId": a.findtext("assignmentId"),
                "serviceRequestId": a.findtext("serviceRequestId"),
                "userIds": [u.text for u in a.findall(".//assignedTo/userId")],
                "comment": a.findtext("assignmentComment"),
                "start": a.findtext("startDate"),
                "end": a.findtext("endDate"),
                "allDay": a.findtext("allDayEvent"),
                "isComplete": a.findtext("isComplete"),
                "created": a.findtext("dateTimeCreated"),
                "completed": a.findtext("dateTimeCompleted"),
            })
        return assignments

    def list_for_user_today(self, user_id: int):
        today = date.today().strftime("%Y.%m.%d")
        start_date = f"{today} 12:00 AM"
        end_date = f"{today} 11:59 PM"
        return self.list_for_user_range(user_id, start_date, end_date)
