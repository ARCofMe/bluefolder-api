# tests/test_materials.py

"""Basic tests for the materials domain client."""

import xml.etree.ElementTree as ET
from bluefolder_api.materials import BlueFolderMaterials


def test_materials_domain():
    m = BlueFolderMaterials()
    assert m.domain == "materials"


def test_materials_list(fake_response):
    m = BlueFolderMaterials()
    m.list({"name": "Filter"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method") is None
    assert xml.find("name").text == "Filter"


def test_materials_get(fake_response):
    m = BlueFolderMaterials()
    m.get({"id": 12})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method") is None
    assert xml.find("id").text == "12"
