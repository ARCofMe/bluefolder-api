# bluefolder_api/appointments.py

import xml.etree.ElementTree as ET
from datetime import date
from .base import BlueFolderBase


class BlueFolderAppointments(BlueFolderBase):
    """
    BlueFolder Appointments API interface.

    Provides helper methods for retrieving appointments within specific
    date ranges or for the current day, as well as transforming BlueFolder
    XML responses into Python dictionaries.

    This class is initialized by the central `BlueFolderClient`, which
    injects a shared `requests.Session`, base URL, and authentication
    credentials.

    Example
    -------
        >>> from bluefolder_api.client import BlueFolderClient
        >>> bf = BlueFolderClient()
        >>> appts = bf.appointments.list_for_user_today(user_id=12345)
        >>> print(appts)
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderAppointments API handler.

        Parameters
        ----------
        client : BlueFolderClient, optional
            The shared client instance that holds authentication and session info.
        """
        super().__init__("appointments", client=client)

    # -------------------------------------------------------------------------
    # Appointment Listing Methods
    # -------------------------------------------------------------------------
    def list_for_user_range(self, user_id: int, start_dt: str, end_dt: str):
        """
        Retrieve all appointments for a given user within a specified date range.

        Constructs and posts an XML request to:
            /api/2.0/appointments/list.aspx

        Parameters
        ----------
        user_id : int
            The BlueFolder user ID.
        start_dt : str
            Start datetime in format `YYYY.MM.DD HH:MM AM/PM`.
        end_dt : str
            End datetime in format `YYYY.MM.DD HH:MM AM/PM`.

        Returns
        -------
        xml.etree.ElementTree.Element
            Parsed XML response element.
        """
        root = ET.Element("request")
        appt_list = ET.SubElement(root, "appointmentList")
        ET.SubElement(appt_list, "dateRangeStart").text = start_dt
        ET.SubElement(appt_list, "dateRangeEnd").text = end_dt
        ET.SubElement(appt_list, "userId").text = str(user_id)

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("list", xml_data=xml_data)

    # -------------------------------------------------------------------------
    def list_for_user_today(self, user_id: int):
        """
        Convenience wrapper for `list_for_user_range()` that retrieves
        all appointments for a user for the current day.

        Parameters
        ----------
        user_id : int
            The BlueFolder user ID.

        Returns
        -------
        xml.etree.ElementTree.Element
            Parsed XML response element for today's appointments.
        """
        today = date.today().strftime("%Y.%m.%d")  # BlueFolder prefers dots
        start = f"{today} 12:00 AM"
        end = f"{today} 11:59 PM"
        return self.list_for_user_range(user_id, start, end)

    # -------------------------------------------------------------------------
    def get_appointments_for_routing(self, user_id: int):
        """
        Extracts and normalizes appointment data for routing purposes.

        Fetches today's appointments via the API and transforms them into
        lightweight Python dictionaries for use in scheduling and mapping
        logic.

        Parameters
        ----------
        user_id : int
            The BlueFolder user ID.

        Returns
        -------
        list[dict]
            A list of appointment dictionaries, each containing:
                - id (str)
                - subject (str)
                - start (str)
                - end (str)
                - userId (str)
        """
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
