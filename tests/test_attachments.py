import xml.etree.ElementTree as ET

from bluefolder_api.attachments import BlueFolderAttachments
from bluefolder_api.exceptions import BlueFolderInvalidResponseError
from bluefolder_api.service_requests import BlueFolderServiceRequests


class DummySession:
    def __init__(self):
        self.calls = []
        self.next_response = None

    def post(self, url, data=None, headers=None, timeout=None):
        self.calls.append({"url": url, "data": data, "headers": headers, "timeout": timeout})
        if self.next_response is not None:
            response = self.next_response
            self.next_response = None
            return response

        class Resp:
            status_code = 200
            content = b"<response status='ok'></response>"
            text = "<response status='ok'></response>"
            headers = {}

        return Resp()


class DummyClient:
    def __init__(self):
        self.base_url = "https://example.bluefolder.com/api/2.0"
        self.session = DummySession()
        self.api_key = "key"
        self.account = "example"


def test_attachment_download_and_delete_builds_xml():
    att = BlueFolderAttachments(client=DummyClient())
    att.download(attachment_token="tok-1")
    xml = ET.fromstring(att.session.calls[-1]["data"])
    assert xml.find(".//attachmentToken").text == "tok-1"

    att.delete(attachment_token="tok-2")
    xml = ET.fromstring(att.session.calls[-1]["data"])
    assert xml.find(".//attachmentToken").text == "tok-2"


def test_attachments_use_shared_api_host_by_default():
    session = DummySession()

    class ClientWithoutBaseUrl:
        def __init__(self, session):
            self.session = session

    client = ClientWithoutBaseUrl(session)
    att = BlueFolderAttachments(client=client)
    att.add_to_service_request(123, "file.txt", "ZmlsZQ==")

    sr = BlueFolderServiceRequests(client=client)
    sr.add(description="desc")

    assert session.calls[0]["url"] == (
        "https://api.bluefolder.com/api/2.0/attachments/add.aspx"
    )
    assert session.calls[1]["url"] == (
        "https://testaccount.bluefolder.com/api/2.0/serviceRequests/add.aspx"
    )


def test_attachments_base_url_can_be_overridden():
    att = BlueFolderAttachments(client=DummyClient(), base_url="https://override.test")
    att.add_to_service_request(123, "file.txt", "ZmlsZQ==")
    assert att.session.calls[-1]["url"] == (
        "https://override.test/attachments/add.aspx"
    )


def test_add_to_service_request_uses_documented_attachment_fields():
    att = BlueFolderAttachments(client=DummyClient())

    att.add_to_service_request(
        123,
        "file.txt",
        "ZmlsZQ==",
        description="hello",
        content_type="text/plain",
    )
    xml = ET.fromstring(att.session.calls[-1]["data"])

    assert xml.find(".//serviceRequestId").text == "123"
    assert xml.find(".//isPublic").text == "false"
    assert xml.find(".//attachmentContent").text == "ZmlsZQ=="
    assert xml.find(".//attachmentFileName").text == "file.txt"
    assert xml.find(".//attachmentDescription").text == "hello"
    assert xml.find(".//attachmentContentType").text == "text/plain"


def test_list_for_service_request_includes_optional_fields(monkeypatch):
    att = BlueFolderAttachments(client=DummyClient())

    xml = ET.fromstring(
        """
        <response>
          <attachmentList>
            <attachment>
              <id>11</id>
              <attachmentToken>tok</attachmentToken>
              <fileName>doc.pdf</fileName>
              <fileType>pdf</fileType>
              <fileSize>0</fileSize>
              <fileLastModified>2024-01-02</fileLastModified>
              <postedOn>2024-01-03</postedOn>
              <private>true</private>
              <isLink>true</isLink>
            </attachment>
          </attachmentList>
        </response>
        """
    )
    monkeypatch.setattr(att, "_post", lambda action, xml_data=None: xml)

    rows = att.list_for_service_request(service_request_id=99)
    assert rows[0]["token"] == "tok"
    assert rows[0]["fileLastModified"] == "2024-01-02"
    assert rows[0]["postedOn"] == "2024-01-03"
    assert rows[0]["private"] == "true"
    assert rows[0]["isLink"] == "true"


def test_list_for_service_request_includes_required_type_filter():
    att = BlueFolderAttachments(client=DummyClient())

    att.list_for_service_request(service_request_id=99)
    xml = ET.fromstring(att.session.calls[-1]["data"])

    assert xml.find(".//type").text == "ServiceRequest"
    assert xml.find(".//serviceRequestId").text == "99"


def test_add_bytes_to_service_request_sanitizes_name_and_infers_type():
    att = BlueFolderAttachments(client=DummyClient())

    att.add_bytes_to_service_request(123, "../bad name?.txt", b"file")
    xml = ET.fromstring(att.session.calls[-1]["data"])

    assert xml.find(".//attachmentFileName").text == ".._bad_name_.txt"
    assert xml.find(".//attachmentContentType").text == "text/plain"


def test_download_returns_binary_payload_when_response_is_not_xml():
    att = BlueFolderAttachments(client=DummyClient())

    class BinaryResp:
        status_code = 200
        content = b"\x89PNG"
        text = ""
        headers = {"Content-Type": "image/png"}

    att.session.next_response = BinaryResp()
    payload = att.download("tok-3")
    assert payload == b"\x89PNG"


def test_download_rejects_empty_payload():
    att = BlueFolderAttachments(client=DummyClient())

    class EmptyResp:
        status_code = 200
        content = b""
        text = ""
        headers = {}

    att.session.next_response = EmptyResp()
    try:
        att.download("tok-4")
        assert False, "expected download to fail"
    except BlueFolderInvalidResponseError:
        pass
