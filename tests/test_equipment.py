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
