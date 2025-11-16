# tests/test_custom_fields.py

""" CustomFields endpoint tests. """

import xml.etree.ElementTree as ET
from bluefolder_api.custom_fields import BlueFolderCustomFields


def test_custom_fields_domain():
    d = BlueFolderCustomFields()
    assert d.domain == "customFields"


def test_custom_fields_list(fake_response):
    d = BlueFolderCustomFields()
    d.list({"serviceRequestId": "200"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("serviceRequestId").text == "200"
