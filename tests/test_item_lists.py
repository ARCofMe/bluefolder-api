# tests/test_item_lists.py

"""ItemLists endpoint tests."""

import xml.etree.ElementTree as ET
from bluefolder_api.item_lists import BlueFolderItemLists


def test_item_lists_domain():
    d = BlueFolderItemLists()
    assert d.domain == "itemLists"


def test_item_lists_list(fake_response):
    d = BlueFolderItemLists()
    d.list({"serviceRequestId": "200"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("serviceRequestId").text == "200"
