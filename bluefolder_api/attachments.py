"""Wrapper around the BlueFolder attachments domain."""

import base64
import mimetypes
import os
import re
import xml.etree.ElementTree as ET
from .base import BlueFolderBase
from .exceptions import BlueFolderInvalidResponseError


class BlueFolderAttachments(BlueFolderBase):
    """
    BlueFolder Attachments API interface.

    Handles attachments (images, documents, etc.) associated with
    Service Requests or Equipment records.
    """

    DEFAULT_BASE_URL = "https://api.bluefolder.com/api/2.0"

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
            use_global_base_url=False,
            use_host_header=False,
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
        ET.SubElement(att_list, "type").text = "ServiceRequest"
        ET.SubElement(att_list, "serviceRequestId").text = str(service_request_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        attachments = []
        for a in xml_response.findall(".//attachment"):
            attachments.append(
                {
                    "id": a.findtext("id"),
                    "token": a.findtext("token") or a.findtext("attachmentToken"),
                    "fileName": a.findtext("fileName"),
                    "fileType": a.findtext("fileType"),
                    "userName": a.findtext("userName"),
                    "dateCreated": a.findtext("dateCreated"),
                    "fileLastModified": a.findtext("fileLastModified")
                    or a.findtext("lastModified"),
                    "postedOn": a.findtext("postedOn"),
                    "fileSize": a.findtext("fileSize"),
                    "description": a.findtext("description"),
                    "private": a.findtext("private") or a.findtext("isPrivate"),
                    "isLink": a.findtext("isLink"),
                }
            )
        return attachments

    @staticmethod
    def _sanitize_filename(file_name: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", (file_name or "").strip())
        return cleaned[:180] or "attachment.bin"

    @staticmethod
    def _coerce_content_type(file_name: str, content_type: str | None) -> str:
        if content_type and "/" in content_type:
            return content_type
        guessed, _ = mimetypes.guess_type(file_name)
        return guessed or "application/octet-stream"

    @staticmethod
    def _max_upload_bytes() -> int:
        raw = os.getenv("BLUEFOLDER_MAX_ATTACHMENT_BYTES") or str(15 * 1024 * 1024)
        return int(raw)

    def add_bytes_to_service_request(
        self,
        service_request_id: int,
        file_name: str,
        file_bytes: bytes,
        description: str = "",
        content_type: str | None = None,
        is_public: bool = False,
    ):
        """Add an attachment from raw bytes with validation and normalization."""
        safe_name = self._sanitize_filename(file_name)
        safe_type = self._coerce_content_type(safe_name, content_type)
        payload = file_bytes if isinstance(file_bytes, bytes) else bytes(file_bytes)
        if len(payload) > self._max_upload_bytes():
            raise ValueError(
                f"Attachment {safe_name} is {len(payload)} bytes, above BLUEFOLDER_MAX_ATTACHMENT_BYTES={self._max_upload_bytes()}."
            )
        encoded = base64.b64encode(payload).decode("ascii")
        return self.add_to_service_request(
            service_request_id=service_request_id,
            file_name=safe_name,
            file_data_base64=encoded,
            description=description,
            content_type=safe_type,
            is_public=is_public,
        )

    # -------------------------------------------------------------------------
    def add_to_service_request(
        self,
        service_request_id: int,
        file_name: str,
        file_data_base64: str,
        description: str = "",
        content_type: str = "application/octet-stream",
        is_public: bool = False,
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
        safe_name = self._sanitize_filename(file_name)
        safe_type = self._coerce_content_type(safe_name, content_type)
        try:
            decoded_size = len(base64.b64decode(file_data_base64, validate=True))
        except Exception as exc:
            raise ValueError("file_data_base64 must be valid base64 data") from exc
        if decoded_size > self._max_upload_bytes():
            raise ValueError(
                f"Attachment {safe_name} is {decoded_size} bytes, above BLUEFOLDER_MAX_ATTACHMENT_BYTES={self._max_upload_bytes()}."
            )
        root = ET.Element("request")
        att_add = ET.SubElement(root, "attachmentAdd")
        ET.SubElement(att_add, "serviceRequestId").text = str(service_request_id)
        ET.SubElement(att_add, "isPublic").text = "true" if is_public else "false"
        ET.SubElement(att_add, "attachmentContent").text = file_data_base64
        ET.SubElement(att_add, "attachmentFileName").text = safe_name
        ET.SubElement(att_add, "attachmentDescription").text = description
        ET.SubElement(att_add, "attachmentContentType").text = safe_type
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        return self._post("add", xml_data=xml_data)

    # -------------------------------------------------------------------------
    def download(self, attachment_token: str):
        """
        Download an attachment file.

        Returns raw XML response containing a Base64-encoded file payload
        per BlueFolder docs.
        """
        root = ET.Element("request")
        att_get = ET.SubElement(root, "attachmentDownload")
        ET.SubElement(att_get, "attachmentToken").text = str(attachment_token)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        response = self._post_response("download", xml_data=xml_data)
        content = getattr(response, "content", b"") or b""
        if not content:
            raise BlueFolderInvalidResponseError("Attachment download returned an empty body")
        if content.lstrip().startswith(b"<"):
            return ET.fromstring(content)
        return content

    def download_content(self, attachment_token: str) -> dict[str, object]:
        """Download one attachment and normalize the payload into bytes plus metadata."""
        payload = self.download(attachment_token)
        if isinstance(payload, (bytes, bytearray)):
            return {
                "content": bytes(payload),
                "content_type": None,
                "file_name": None,
                "source": "binary",
            }

        content_node = payload.find(".//attachmentContent")
        if content_node is None:
            content_node = payload.find(".//fileContent")
        if content_node is None:
            content_node = payload.find(".//content")
        if content_node is None or not (content_node.text or "").strip():
            raise BlueFolderInvalidResponseError("Attachment XML response did not include attachment content")
        try:
            decoded = base64.b64decode((content_node.text or "").strip(), validate=True)
        except Exception as exc:
            raise BlueFolderInvalidResponseError("Attachment XML response did not contain valid base64 content") from exc
        return {
            "content": decoded,
            "content_type": payload.findtext(".//attachmentContentType") or payload.findtext(".//contentType"),
            "file_name": payload.findtext(".//attachmentFileName") or payload.findtext(".//fileName"),
            "source": "xml",
        }

    def delete(self, attachment_token: str):
        """Delete an attachment by ID."""
        root = ET.Element("request")
        att_del = ET.SubElement(root, "attachmentDelete")
        ET.SubElement(att_del, "attachmentToken").text = str(attachment_token)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("delete", xml_data=xml_data)
