import xml.etree.ElementTree as ET

from bluefolder_api.attachments import BlueFolderAttachments


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
