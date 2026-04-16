"""Helpers for working with BlueFolder comments."""

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderComments(BlueFolderBase):
    """
    BlueFolder Comments API interface.

    Handles creation and listing of comments or notes attached to
    Service Requests, Equipment, or other entities.
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderComments API handler.
        """
        super().__init__("comments", client=client)

    # -------------------------------------------------------------------------
    def list_for_service_request(self, service_request_id: int):
        """
        Retrieve all comments associated with a Service Request.

        Parameters
        ----------
        service_request_id : int
            Numeric Service Request ID.

        Returns
        -------
        list[dict]
            List of comment records (author, date, text, visibility).
        """
        service_request_id = self._validate_positive_id(service_request_id, "service_request_id")
        root = ET.Element("request")
        comment_list = ET.SubElement(root, "commentList")
        ET.SubElement(comment_list, "serviceRequestId").text = str(service_request_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        comments = []
        for c in xml_response.findall(".//comment"):
            comments.append(
                {
                    "id": c.findtext("id"),
                    "author": c.findtext("userName"),
                    "dateCreated": c.findtext("dateCreated"),
                    "text": c.findtext("commentText"),
                    "isVisibleToCustomer": self._parse_bool(c.findtext("isVisibleToCustomer")),
                }
            )
        return comments

    # -------------------------------------------------------------------------
    def add_to_service_request(
        self, service_request_id: int, text: str, visible_to_customer: bool = False
    ):
        """
        Add a comment to a Service Request.

        Parameters
        ----------
        service_request_id : int
            Target Service Request ID.
        text : str
            Comment body text.
        visible_to_customer : bool, default False
            Whether the comment is visible to the customer portal.

        Returns
        -------
        xml.etree.ElementTree.Element
            Raw XML response from BlueFolder.
        """
        service_request_id = self._validate_positive_id(service_request_id, "service_request_id")
        text = str(text or "").strip()
        if not text:
            raise ValueError("comment text is required")

        root = ET.Element("request")
        comment_add = ET.SubElement(root, "commentAdd")
        ET.SubElement(comment_add, "serviceRequestId").text = str(service_request_id)
        ET.SubElement(comment_add, "commentText").text = text
        ET.SubElement(comment_add, "isVisibleToCustomer").text = (
            "1" if visible_to_customer else "0"
        )
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        return self._post("add", xml_data=xml_data)

    @staticmethod
    def _validate_positive_id(value: int, field_name: str) -> int:
        try:
            normalized = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} must be a positive integer") from exc
        if normalized <= 0:
            raise ValueError(f"{field_name} must be a positive integer")
        return normalized

    @staticmethod
    def _parse_bool(value: str | None) -> bool:
        return str(value or "").strip().lower() in {"1", "true", "yes", "y"}
