import xml.etree.ElementTree as ET

from bluefolder_api.attachments import BlueFolderAttachments
from bluefolder_api.service_requests import BlueFolderServiceRequests


class DummySession:
    def __init__(self):
        self.calls = []

    def post(self, url, data=None, headers=None, timeout=None):
        self.calls.append({"url": url, "data": data})

        class Resp:
            status_code = 200
            content = b"<response status='ok'></response>"
            text = "<response status='ok'></response>"

        return Resp()


class DummyClient:
    def __init__(self):
        self.base_url = "https://example.bluefolder.com/api/2.0"
        self.session = DummySession()
        self.api_key = "key"
        self.account = "example"


def test_attachment_download_and_delete_builds_xml():
    att = BlueFolderAttachments(client=DummyClient())
    att.download(attachment_id=1)
    xml = ET.fromstring(att.session.calls[-1]["data"])
    assert xml.find(".//attachmentId").text == "1"

    att.delete(attachment_id=2)
    xml = ET.fromstring(att.session.calls[-1]["data"])
    assert xml.find(".//attachmentId").text == "2"


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
