# bluefolder_api/assignments.py

import xml.etree.ElementTree as ET
from datetime import date
from .base import BlueFolderBase


class BlueFolderAssignments(BlueFolderBase):
    """
    BlueFolder Assignments API interface.

    Handles retrieval of Service Request Assignments for specific users and
    date ranges. This module is especially useful for routing and scheduling
    systems that need to determine which service requests a technician is
    assigned to for a given day.

    This endpoint lives under the `/serviceRequests` domain but uses a unique
    action path (`getAssignmentList.aspx`).

    Example
    -------
        >>> from bluefolder_api.client import BlueFolderClient
        >>> bf = BlueFolderClient()
        >>> assignments = bf.assignments.list_for_user_today(33538043)
        >>> print(assignments)
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderAssignments API handler.

        Parameters
        ----------
        client : BlueFolderClient, optional
            Shared client instance containing base_url, API key, and session.
        """
        super().__init__("serviceRequests", client=client)

    # -------------------------------------------------------------------------
    # Assignment Listing Methods
    # -------------------------------------------------------------------------
    def list_for_user_range(
        self,
        user_id: int,
        start_date: str,
        end_date: str,
        date_range_type: str = "scheduled",
    ):
        """
        Retrieve a list of service request assignments for a user within a specific date range.

        Constructs and sends a POST request to:
            /api/2.0/serviceRequests/getAssignmentList.aspx

        Parameters
        ----------
        user_id : int
            The BlueFolder user ID whose assignments should be retrieved.
        start_date : str
            Start of the date range in BlueFolder format (e.g. "2025.11.07 12:00 AM").
        end_date : str
            End of the date range in BlueFolder format (e.g. "2025.11.07 11:59 PM").
        date_range_type : str, optional
            The type of date to filter on. Valid values include:
                - "scheduled" (default)
                - "created"
                - "completed"

        Returns
        -------
        list[dict]
            A list of assignment dictionaries containing:
                - assignmentId (str)
                - serviceRequestId (str)
                - userIds (list[str])
                - comment (str)
                - start (str)
                - end (str)
                - allDay (str)
                - isComplete (str)
                - created (str)
                - completed (str)
        """
        # Build XML request body
        root = ET.Element("request")
        sr_assign_list = ET.SubElement(root, "serviceRequestAssignmentList")

        # Core date filters
        ET.SubElement(sr_assign_list, "dateRangeStart").text = start_date
        ET.SubElement(sr_assign_list, "dateRangeEnd").text = end_date
        ET.SubElement(sr_assign_list, "dateRangeType").text = date_range_type

        # Assigned user filter
        assigned_to = ET.SubElement(sr_assign_list, "assignedTo")
        ET.SubElement(assigned_to, "userId").text = str(user_id)

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        # Endpoint override since Assignments use a special URL pattern
        url_override = f"{self.base_url}/serviceRequests/getAssignmentList.aspx"

        xml_response = self._post(
            "getAssignmentList",
            xml_data=xml_data,
            override_url=url_override,
        )

        assignments = []
        for a in xml_response.findall(".//serviceRequestAssignment"):
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

    # -------------------------------------------------------------------------
    def list_for_user_today(self, user_id: int):
        """
        Convenience wrapper to list all assignments for a given user for today.

        Parameters
        ----------
        user_id : int
            The BlueFolder user ID.

        Returns
        -------
        list[dict]
            A list of assignment dictionaries for the current day.
        """
        today = date.today().strftime("%Y.%m.%d")
        start_date = f"{today} 12:00 AM"
        end_date = f"{today} 11:59 PM"
        return self.list_for_user_range(user_id, start_date, end_date)
