import xml.etree.ElementTree as ET

from bluefolder_api.items import BlueFolderItems


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


def test_items_add_edit_delete_get_list():
    items = BlueFolderItems(client=DummyClient())

    items.add(name="Widget", sku="W1")
    xml = ET.fromstring(items.session.calls[-1]["data"])
    assert xml.find(".//name").text == "Widget"
    assert xml.find(".//sku").text == "W1"

    items.edit(item_id=2, name="Widget v2")
    xml = ET.fromstring(items.session.calls[-1]["data"])
    assert xml.find(".//itemId").text == "2"
    assert xml.find(".//name").text == "Widget v2"

    items.get(item_id=3)
    xml = ET.fromstring(items.session.calls[-1]["data"])
    assert xml.find(".//itemId").text == "3"

    items.delete(item_id=4)
    xml = ET.fromstring(items.session.calls[-1]["data"])
    assert xml.find(".//itemId").text == "4"

    items.list(itemListId=1)
    xml = ET.fromstring(items.session.calls[-1]["data"])
    assert xml.find(".//itemListId").text == "1"
