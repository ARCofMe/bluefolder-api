# tests/test_assignments.py

""" Assignments endpoint tests. """

import xml.etree.ElementTree as ET
from bluefolder_api.assignments import BlueFolderAssignments


def test_assignments_domain():
    a = BlueFolderAssignments()
    assert a.domain == "assignments"


def test_assignments_list_for_user(fake_response):
    a = BlueFolderAssignments()
    a.list_for_user({"userId": 7})

    assert fake_response.called
    assert fake_response.last_url.endswith(
        "/assignments/list.aspx"
    )

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("userId").text == "7"
