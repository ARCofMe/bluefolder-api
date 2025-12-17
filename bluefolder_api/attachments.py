"""Wrapper around the BlueFolder attachments domain."""

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderAttachments(BlueFolderBase):
    """
    BlueFolder Attachments API interface.

    Handles attachments (images, documents, etc.) associated with
    Service Requests or Equipment records.
    """

    DEFAULT_BASE_URL = "https://app.bluefolder.com/api/2.0"

    def __init__(self, client=None, base_url: str | None = None):
        """
        Initialize the BlueFolderAttachments API handler.
        """
        super().__init__(
            "attachments",
            client=client,
            domain_base_url=base_url,
            domain_base_env="BLUEFOLDER_ATTACHMENTS_BASE_URL",
            default_base_url=self.DEFAULT_BASE_URL,
        )

    # -------------------------------------------------------------------------
    def list_for_service_request(self, service_request_id: int):
        """
        Retrieve attachments linked to a Service Request.

        Parameters
        ----------
        service_request_id : int
            Numeric Service Request ID.

        Returns
        -------
        list[dict]
            List of attachment metadata.
        """
        root = ET.Element("request")
        att_list = ET.SubElement(root, "attachmentList")
        ET.SubElement(att_list, "serviceRequestId").text = str(service_request_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        attachments = []
        for a in xml_response.findall(".//attachment"):
            attachments.append(
                {
                    "id": a.findtext("id"),
                    "fileName": a.findtext("fileName"),
                    "fileType": a.findtext("fileType"),
                    "userName": a.findtext("userName"),
                    "dateCreated": a.findtext("dateCreated"),
                    "fileSize": a.findtext("fileSize"),
                    "description": a.findtext("description"),
                }
            )
        return attachments

    # -------------------------------------------------------------------------
    def add_to_service_request(
        self,
        service_request_id: int,
        file_name: str,
        file_data_base64: str,
        description: str = "",
    ):
        """
        Add an attachment to a Service Request.

        Parameters
        ----------
        service_request_id : int
            Service Request ID.
        file_name : str
            File name (e.g., 'invoice.pdf').
        file_data_base64 : str
            Base64-encoded file contents.
        description : str, optional
            Optional description or note.

        Returns
        -------
        xml.etree.ElementTree.Element
            Raw XML response.
        """
        root = ET.Element("request")
        att_add = ET.SubElement(root, "attachmentAdd")
        ET.SubElement(att_add, "serviceRequestId").text = str(service_request_id)
        ET.SubElement(att_add, "fileName").text = file_name
        ET.SubElement(att_add, "fileData").text = file_data_base64
        ET.SubElement(att_add, "description").text = description
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        return self._post("add", xml_data=xml_data)

    # -------------------------------------------------------------------------
    def download(self, attachment_id: int):
        """
        Download an attachment file.

        Returns raw XML response containing a Base64-encoded file payload
        per BlueFolder docs.
        """
        root = ET.Element("request")
        att_get = ET.SubElement(root, "attachmentDownload")
        ET.SubElement(att_get, "attachmentId").text = str(attachment_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("download", xml_data=xml_data)

    def delete(self, attachment_id: int):
        """Delete an attachment by ID."""
        root = ET.Element("request")
        att_del = ET.SubElement(root, "attachmentDelete")
        ET.SubElement(att_del, "attachmentId").text = str(attachment_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("delete", xml_data=xml_data)
