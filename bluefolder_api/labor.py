"""Labor entry utilities for the BlueFolder API."""

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderLabor(BlueFolderBase):
    """
    BlueFolder Labor API interface.

    Provides access to labor entries logged against Service Requests,
    including time tracking, user attribution, and billing information.
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderLabor API handler.
        """
        super().__init__("labor", client=client)

    # -------------------------------------------------------------------------
    def list_for_service_request(self, service_request_id: int):
        """
        Retrieve all labor entries for a given Service Request.

        Parameters
        ----------
        service_request_id : int
            Numeric Service Request ID.

        Returns
        -------
        list[dict]
            List of labor entries.
        """
        root = ET.Element("request")
        labor_list = ET.SubElement(root, "laborList")
        ET.SubElement(labor_list, "serviceRequestId").text = str(service_request_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        labor_entries = []
        for l in xml_response.findall(".//labor"):
            labor_entries.append(
                {
                    "id": l.findtext("id"),
                    "userId": l.findtext("userId"),
                    "date": l.findtext("dateWorked"),
                    "hours": l.findtext("hoursWorked"),
                    "rate": l.findtext("hourlyRate"),
                    "total": l.findtext("total"),
                    "isBillable": l.findtext("isBillable") == "1",
                    "description": l.findtext("description") or "",
                }
            )
        return labor_entries

    # -------------------------------------------------------------------------
    def add_to_service_request(
        self,
        service_request_id: int,
        user_id: int,
        hours: float,
        date_worked: str,
        description: str = "",
        is_billable: bool = True,
    ):
        """
        Add a labor entry to a Service Request.

        Parameters
        ----------
        service_request_id : int
            Target Service Request ID.
        user_id : int
            ID of the technician/user who performed the work.
        hours : float
            Number of hours worked.
        date_worked : str
            Date worked, formatted as 'YYYY.MM.DD'.
        description : str, optional
            Description of the work performed.
        is_billable : bool, default True
            Whether this labor entry is billable to the customer.

        Returns
        -------
        xml.etree.ElementTree.Element
            Raw XML response from BlueFolder.
        """
        root = ET.Element("request")
        labor_add = ET.SubElement(root, "laborAdd")
        ET.SubElement(labor_add, "serviceRequestId").text = str(service_request_id)
        ET.SubElement(labor_add, "userId").text = str(user_id)
        ET.SubElement(labor_add, "hoursWorked").text = str(hours)
        ET.SubElement(labor_add, "dateWorked").text = date_worked
        ET.SubElement(labor_add, "description").text = description
        ET.SubElement(labor_add, "isBillable").text = "1" if is_billable else "0"
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        return self._post("add", xml_data=xml_data)
