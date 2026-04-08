# tests/test_labor.py

"""Labor endpoint tests."""

import xml.etree.ElementTree as ET
from bluefolder_api.labor import BlueFolderLabor


def test_labor_domain():
    d = BlueFolderLabor()
    assert d.domain == "labor"


def test_labor_list(fake_response):
    d = BlueFolderLabor()
    d.list({"serviceRequestId": "200"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method") is None
    assert xml.find("serviceRequestId").text == "200"
