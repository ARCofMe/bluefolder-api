# bluefolder_api/comments.py

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
        root = ET.Element("request")
        comment_list = ET.SubElement(root, "commentList")
        ET.SubElement(comment_list, "serviceRequestId").text = str(service_request_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        comments = []
        for c in xml_response.findall(".//comment"):
            comments.append({
                "id": c.findtext("id"),
                "author": c.findtext("userName"),
                "dateCreated": c.findtext("dateCreated"),
                "text": c.findtext("commentText"),
                "isVisibleToCustomer": c.findtext("isVisibleToCustomer") == "1",
            })
        return comments

    # -------------------------------------------------------------------------
    def add_to_service_request(self, service_request_id: int, text: str, visible_to_customer: bool = False):
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
        root = ET.Element("request")
        comment_add = ET.SubElement(root, "commentAdd")
        ET.SubElement(comment_add, "serviceRequestId").text = str(service_request_id)
        ET.SubElement(comment_add, "commentText").text = text
        ET.SubElement(comment_add, "isVisibleToCustomer").text = "1" if visible_to_customer else "0"
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        return self._post("add", xml_data=xml_data)
