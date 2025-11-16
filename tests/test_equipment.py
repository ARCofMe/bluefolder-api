# tests/test_equipment.py

"""Smoke tests for the equipment domain client."""

import xml.etree.ElementTree as ET
from bluefolder_api.equipment import BlueFolderEquipment


def test_equipment_domain():
    e = BlueFolderEquipment()
    assert e.domain == "equipment"


def test_equipment_list(fake_response):
    e = BlueFolderEquipment()
    e.list({"customerId": 55})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("customerId").text == "55"


def test_equipment_get(fake_response):
    e = BlueFolderEquipment()
    e.get({"id": 333})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "get"
    assert xml.find("id").text == "333"


# Mutation coverage
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


def test_equipment_add_edit_list_all():
    eq = BlueFolderEquipment(client=DummyClient())

    eq.add(customer_id=1, name="Furnace", model="X1")
    xml = ET.fromstring(eq.session.calls[-1]["data"])
    assert xml.find(".//customerId").text == "1"
    assert xml.find(".//name").text == "Furnace"
    assert xml.find(".//model").text == "X1"

    eq.edit(equipment_id=10, name="Updated")
    xml = ET.fromstring(eq.session.calls[-1]["data"])
    assert xml.find(".//equipmentId").text == "10"
    assert xml.find(".//name").text == "Updated"

    eq.list_all()
    assert eq.session.calls[-1]["url"].endswith("/equipment/list.aspx")
