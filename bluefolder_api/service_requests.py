"""BlueFolder service request listing helpers."""

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderServiceRequests(BlueFolderBase):
    """
    BlueFolder Service Requests API interface.

    Handles retrieval of Service Requests from the BlueFolder API, including
    filtering by assigned user, date range, and date field type.

    This class provides helper methods for:
      • Listing all service requests for a user within a time window.
      • Listing all service requests in a global date range.
      • Fetching a single service request by ID.

    Example
    -------
        >>> from bluefolder_api.client import BlueFolderClient
        >>> bf = BlueFolderClient()
        >>> srs = bf.service_requests.list_for_user_range(33538043, "2025.11.07 12:00 AM", "2025.11.07 11:59 PM")
        >>> print(srs)
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderServiceRequests API handler.

        Parameters
        ----------
        client : BlueFolderClient, optional
            Shared client instance containing base_url, API key, and session.
        """
        super().__init__("serviceRequests", client=client)

    # -------------------------------------------------------------------------
    # LIST METHODS
    # -------------------------------------------------------------------------
    def list_for_user_range(
        self,
        user_id: int,
        start_date: str,
        end_date: str,
        date_range_type: str = "dateTimeCreated",
    ):
        """
        Retrieve a list of Service Requests assigned to a specific user within a date range.

        Constructs and posts an XML request to:
            /api/2.0/serviceRequests/list.aspx

        Parameters
        ----------
        user_id : int
            BlueFolder user ID whose assigned service requests should be returned.
        start_date : str
            Start date/time of the query range (e.g. "2025.11.07 12:00 AM").
        end_date : str
            End date/time of the query range (e.g. "2025.11.07 11:59 PM").
        date_range_type : str, optional
            Specifies which date field to filter by. Valid values include:
                - "dateTimeCreated"
                - "dateTimeClosed"
                - "dateTimeScheduled" (if supported by your tenant)

        Returns
        -------
        list[dict]
            List of service request dictionaries containing:
                - id (str)
                - subject (str)
                - customerId (str)
                - address, city, state, zip
                - start, end
                - userIds (list[str])
        """
        root = ET.Element("request")
        sr_list = ET.SubElement(root, "serviceRequestList")

        # Filter by assigned user
        assigned_to = ET.SubElement(sr_list, "assignedTo")
        ET.SubElement(assigned_to, "userId").text = str(user_id)

        # Use <dateRange> with dateField attribute
        date_range = ET.SubElement(sr_list, "dateRange", {"dateField": date_range_type})
        ET.SubElement(date_range, "dateRangeStart").text = start_date
        ET.SubElement(date_range, "dateRangeEnd").text = end_date

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        requests = []

        for sr in xml_response.findall(".//serviceRequest"):
            requests.append(
                {
                    "id": sr.findtext("id"),
                    "subject": sr.findtext("subject"),
                    "customerId": sr.findtext("customerId"),
                    "address": sr.findtext("locationAddress"),
                    "city": sr.findtext("locationCity"),
                    "state": sr.findtext("locationState"),
                    "zip": sr.findtext("locationZip"),
                    "start": sr.findtext("dateTimeStart"),
                    "end": sr.findtext("dateTimeEnd"),
                    "userIds": [u.text for u in sr.findall(".//assignedTo/userId")],
                }
            )
        return requests

    # -------------------------------------------------------------------------
    def list_for_range(
        self,
        start_date: str,
        end_date: str,
        date_field: str = "dateTimeCreated",
    ):
        """
        Retrieve all Service Requests within a given date range (no user filter).

        Constructs and posts an XML request to:
            /api/2.0/serviceRequests/list.aspx

        Parameters
        ----------
        start_date : str
            Start date/time of the query range (e.g. "2025.11.07 12:00 AM").
        end_date : str
            End date/time of the query range (e.g. "2025.11.07 11:59 PM").
        date_field : str, optional
            The date field to filter by. Default is "dateTimeCreated".

        Returns
        -------
        list[dict]
            List of service request dictionaries containing:
                - id, subject, customerId
                - address, city, state, zip
                - start, end
        """
        root = ET.Element("request")
        sr_list = ET.SubElement(root, "serviceRequestList")

        date_range = ET.SubElement(sr_list, "dateRange", {"dateField": date_field})
        ET.SubElement(date_range, "dateRangeStart").text = start_date
        ET.SubElement(date_range, "dateRangeEnd").text = end_date

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        requests = []

        for sr in xml_response.findall(".//serviceRequest"):
            requests.append(
                {
                    "id": sr.findtext("id"),
                    "subject": sr.findtext("subject"),
                    "customerId": sr.findtext("customerId"),
                    "address": sr.findtext("locationAddress"),
                    "city": sr.findtext("locationCity"),
                    "state": sr.findtext("locationState"),
                    "zip": sr.findtext("locationZip"),
                    "start": sr.findtext("dateTimeStart"),
                    "end": sr.findtext("dateTimeEnd"),
                }
            )
        return requests

    # -------------------------------------------------------------------------
    def get_by_id(self, sr_id: int):
        """
        Retrieve a single Service Request by ID.

        Constructs and posts an XML request to:
            /api/2.0/serviceRequests/get.aspx

        Parameters
        ----------
        sr_id : int
            The numeric Service Request ID to retrieve.

        Returns
        -------
        xml.etree.ElementTree.Element
            Parsed XML response for the requested service request.
        """
        root = ET.Element("request")
        sr_get = ET.SubElement(root, "serviceRequestGet")
        ET.SubElement(sr_get, "serviceRequestId").text = str(sr_id)

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("get", xml_data=xml_data)
