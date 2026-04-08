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
    # CREATE / UPDATE / DELETE
    # -------------------------------------------------------------------------
    def add(self, **fields):
        """
        Create a new Service Request.

        Accepts arbitrary keyword args mapped to XML elements inside
        <serviceRequestAdd>. Examples include description, customerId,
        customerLocationId, priority, status, dueDate, externalId, etc.

        Special handling:
        - customFields: dict of {name: value}
        - equipmentToService: iterable of equipmentId values
        """
        root = ET.Element("request")
        sr_add = ET.SubElement(root, "serviceRequestAdd")
        self._populate_common_fields(sr_add, fields)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("add", xml_data=xml_data)

    def edit(
        self,
        service_request_id: int | None = None,
        external_id: str | None = None,
        **fields,
    ):
        """
        Update an existing Service Request by id or externalId.

        Required: service_request_id or external_id.
        Special handling matches `add()`.
        """
        if not service_request_id and not external_id:
            raise ValueError("service_request_id or external_id is required")

        root = ET.Element("request")
        sr_edit = ET.SubElement(root, "serviceRequestEdit")
        if service_request_id:
            ET.SubElement(sr_edit, "serviceRequestId").text = str(service_request_id)
        if external_id:
            ET.SubElement(sr_edit, "externalId").text = external_id
        self._populate_common_fields(sr_edit, fields)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("edit", xml_data=xml_data)

    def delete(
        self, service_request_id: int | None = None, external_id: str | None = None
    ):
        """Delete a Service Request by id or externalId."""
        if not service_request_id and not external_id:
            raise ValueError("service_request_id or external_id is required")
        root = ET.Element("request")
        sr_del = ET.SubElement(root, "serviceRequestDelete")
        if service_request_id:
            ET.SubElement(sr_del, "serviceRequestId").text = str(service_request_id)
        if external_id:
            ET.SubElement(sr_del, "externalId").text = external_id
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("delete", xml_data=xml_data)

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
        # Ensure values are strings before serializing XML (avoid TypeError when ints are passed)
        ET.SubElement(date_range, "dateRangeStart").text = str(start_date)
        ET.SubElement(date_range, "dateRangeEnd").text = str(end_date)

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        requests = []

        for sr in xml_response.findall(".//serviceRequest"):
            requests.append(
                {
                    "id": sr.findtext("id"),
                    "subject": sr.findtext("subject"),
                    "status": sr.findtext("serviceRequestStatus"),
                    "statusName": sr.findtext("serviceRequestStatusName"),
                    "customerId": sr.findtext("customerId"),
                    "externalId": sr.findtext("externalId"),
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
        # Cast to str to avoid xml serialization errors if callers pass non-string values
        ET.SubElement(date_range, "dateRangeStart").text = str(start_date)
        ET.SubElement(date_range, "dateRangeEnd").text = str(end_date)

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        requests = []

        for sr in xml_response.findall(".//serviceRequest"):
            requests.append(
                {
                    "id": sr.findtext("id"),
                    "subject": sr.findtext("subject"),
                    "status": sr.findtext("serviceRequestStatus"),
                    "statusName": sr.findtext("serviceRequestStatusName"),
                    "customerId": sr.findtext("customerId"),
                    "externalId": sr.findtext("externalId"),
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

    def get_history(self, service_request_id: int):
        """Retrieve the history for a Service Request."""
        root = ET.Element("request")
        sr_hist = ET.SubElement(root, "serviceRequestHistory")
        ET.SubElement(sr_hist, "serviceRequestId").text = str(service_request_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("getHistory", xml_data=xml_data)

    # -------------------------------------------------------------------------
    # ASSIGNMENT OPERATIONS
    # -------------------------------------------------------------------------
    def add_assignment(
        self,
        service_request_id: int,
        assignee_user_ids: list[int] | tuple[int, ...],
        start_date: str | None = None,
        end_date: str | None = None,
        all_day_event: bool | None = None,
        assignment_comment: str | None = None,
    ):
        """Add an assignment to a Service Request."""
        root = ET.Element("request")
        sr_add = ET.SubElement(root, "serviceRequestAssignmentAdd")
        ET.SubElement(sr_add, "serviceRequestId").text = str(service_request_id)
        if start_date:
            ET.SubElement(sr_add, "startDate").text = start_date
        if end_date:
            ET.SubElement(sr_add, "endDate").text = end_date
        if all_day_event is not None:
            ET.SubElement(sr_add, "allDayEvent").text = str(all_day_event).lower()
        if assignment_comment:
            ET.SubElement(sr_add, "assignmentComment").text = assignment_comment
        assignees = ET.SubElement(sr_add, "assignedTo")
        for uid in assignee_user_ids:
            ET.SubElement(assignees, "userId").text = str(uid)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("addAssignment", xml_data=xml_data)

    def edit_assignment(self, assignment_id: int, **fields):
        """
        Edit an existing assignment. Supports startDate, endDate,
        allDayEvent, assignmentComment, assigneeUserIds (list[int]).
        """
        root = ET.Element("request")
        sr_edit = ET.SubElement(root, "serviceRequestAssignmentEdit")
        ET.SubElement(sr_edit, "assignmentId").text = str(assignment_id)
        if "startDate" in fields:
            ET.SubElement(sr_edit, "startDate").text = fields["startDate"]
        if "endDate" in fields:
            ET.SubElement(sr_edit, "endDate").text = fields["endDate"]
        if "allDayEvent" in fields:
            ET.SubElement(sr_edit, "allDayEvent").text = str(
                fields["allDayEvent"]
            ).lower()
        if "assignmentComment" in fields:
            ET.SubElement(sr_edit, "assignmentComment").text = fields[
                "assignmentComment"
            ]
        if "assigneeUserIds" in fields:
            assignees = ET.SubElement(sr_edit, "assignedTo")
            for uid in fields["assigneeUserIds"]:
                ET.SubElement(assignees, "userId").text = str(uid)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("editAssignment", xml_data=xml_data)

    def delete_assignment(self, assignment_id: int):
        """Delete an assignment from a Service Request."""
        root = ET.Element("request")
        sr_del = ET.SubElement(root, "serviceRequestDeleteAssignment")
        ET.SubElement(sr_del, "assignmentId").text = str(assignment_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("deleteAssignment", xml_data=xml_data)

    def complete_assignment(self, assignment_id: int, comment: str | None = None):
        """Mark an assignment complete."""
        root = ET.Element("request")
        sr_comp = ET.SubElement(root, "serviceRequestAssignmentComplete")
        ET.SubElement(sr_comp, "assignmentId").text = str(assignment_id)
        if comment:
            ET.SubElement(sr_comp, "completionComment").text = comment
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("completeAssignment", xml_data=xml_data)

    # -------------------------------------------------------------------------
    # COMMENTS / LABOR / MATERIALS SHORTCUTS
    # -------------------------------------------------------------------------
    def add_comment(
        self,
        service_request_id: int,
        text: str,
        comment_is_public: bool | None = None,
        user_id: int | None = None,
    ):
        """Add a comment to a Service Request."""
        root = ET.Element("request")
        sr_comment = ET.SubElement(root, "serviceRequestAddComment")
        ET.SubElement(sr_comment, "serviceRequestId").text = str(service_request_id)
        ET.SubElement(sr_comment, "comment").text = text
        if user_id is not None:
            ET.SubElement(sr_comment, "userId").text = str(user_id)
        if comment_is_public is not None:
            ET.SubElement(sr_comment, "commentIsPublic").text = str(
                comment_is_public
            ).lower()
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("addComment", xml_data=xml_data)

    def add_labor(self, service_request_id: int, user_id: int, duration: str, **fields):
        """
        Add a labor entry to a Service Request.

        Required: service_request_id, user_id, duration.
        Optional fields: dateWorked, startTime, comment, itemId, itemDescription,
        billable, commentIsPublic, etc.
        """
        root = ET.Element("request")
        sr_labor = ET.SubElement(root, "serviceRequestAddLabor")
        ET.SubElement(sr_labor, "serviceRequestId").text = str(service_request_id)
        ET.SubElement(sr_labor, "userId").text = str(user_id)
        ET.SubElement(sr_labor, "duration").text = duration
        for key, val in fields.items():
            ET.SubElement(sr_labor, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("addLabor", xml_data=xml_data)

    def edit_labor(self, labor_id: int, **fields):
        """Edit an existing labor item on a Service Request."""
        root = ET.Element("request")
        sr_labor = ET.SubElement(root, "serviceRequestEditLabor")
        ET.SubElement(sr_labor, "laborId").text = str(labor_id)
        for key, val in fields.items():
            ET.SubElement(sr_labor, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("editLabor", xml_data=xml_data)

    def add_material(
        self, service_request_id: int, item_id: int, item_quantity: int, **fields
    ):
        """Add a materials line to a Service Request."""
        root = ET.Element("request")
        sr_mat = ET.SubElement(root, "serviceRequestAddMaterial")
        ET.SubElement(sr_mat, "serviceRequestId").text = str(service_request_id)
        ET.SubElement(sr_mat, "itemId").text = str(item_id)
        ET.SubElement(sr_mat, "itemQuantity").text = str(item_quantity)
        for key, val in fields.items():
            ET.SubElement(sr_mat, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("addMaterial", xml_data=xml_data)

    def edit_material(self, material_id: int, **fields):
        """Edit a materials line on a Service Request."""
        root = ET.Element("request")
        sr_mat = ET.SubElement(root, "serviceRequestEditMaterial")
        ET.SubElement(sr_mat, "materialId").text = str(material_id)
        for key, val in fields.items():
            ET.SubElement(sr_mat, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("editMaterial", xml_data=xml_data)

    # -------------------------------------------------------------------------
    # INTERNAL HELPERS
    # -------------------------------------------------------------------------
    def _populate_common_fields(self, node: ET.Element, fields: dict):
        """Attach common service request fields (description, priority, etc.)."""
        # Custom fields
        custom_fields = fields.pop("customFields", None) or fields.pop(
            "custom_fields", None
        )
        if custom_fields:
            cf_parent = ET.SubElement(node, "customFields")
            for name, val in custom_fields.items():
                ET.SubElement(cf_parent, "customField", {"name": str(name)}).text = str(
                    val
                )

        # Equipment list
        equipment_list = fields.pop("equipmentToService", None) or fields.pop(
            "equipment_to_service", None
        )
        if equipment_list:
            equipment_parent = ET.SubElement(node, "equipmentToService")
            for eq_id in equipment_list:
                ET.SubElement(equipment_parent, "equipmentId").text = str(eq_id)

        for key, val in fields.items():
            if val is None:
                continue
            ET.SubElement(node, key).text = str(val)
