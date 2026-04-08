# tests/test_comments.py

"""Comments endpoint tests."""

import xml.etree.ElementTree as ET
from bluefolder_api.comments import BlueFolderComments


def test_comments_domain():
    d = BlueFolderComments()
    assert d.domain == "comments"


def test_comments_list(fake_response):
    d = BlueFolderComments()
    d.list({"serviceRequestId": "200"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method") is None
    assert xml.find("serviceRequestId").text == "200"
