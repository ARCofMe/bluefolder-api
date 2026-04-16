# tests/test_assignments.py

"""Assignments endpoint tests."""

import xml.etree.ElementTree as ET
from bluefolder_api.assignments import BlueFolderAssignments


def test_assignments_domain():
    a = BlueFolderAssignments()
    assert a.domain == "assignments"


def test_assignments_list_for_user(fake_response):
    a = BlueFolderAssignments()
    a.list_for_user({"userId": 7})

    assert fake_response.called
    assert fake_response.last_url.endswith("/assignments/list.aspx")

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method") is None
    assert xml.find("userId").text == "7"


def test_assignments_list_for_user_range_preserves_location_context(monkeypatch):
    root = ET.Element("response")
    assignment = ET.SubElement(root, "serviceRequestAssignment")
    ET.SubElement(assignment, "assignmentId").text = "a-1"
    ET.SubElement(assignment, "serviceRequestId").text = "96268"
    assigned_to = ET.SubElement(assignment, "assignedTo")
    ET.SubElement(assigned_to, "userId").text = "13051"
    ET.SubElement(assignment, "assignmentComment").text = "AM stop"
    ET.SubElement(assignment, "startDate").text = "2026.04.16 08:00 AM"
    ET.SubElement(assignment, "endDate").text = "2026.04.16 10:00 AM"
    ET.SubElement(assignment, "allDayEvent").text = "false"
    ET.SubElement(assignment, "isComplete").text = "true"
    ET.SubElement(assignment, "addressStreet").text = "180 E Hebron Rd"
    ET.SubElement(assignment, "addressCity").text = "Hebron"
    ET.SubElement(assignment, "addressState").text = "ME"
    ET.SubElement(assignment, "addressPostalCode").text = "04238"

    def fake_post(self, action, **kwargs):
        assert action == "getAssignmentList"
        assert kwargs["override_url"].endswith("/serviceRequests/getAssignmentList.aspx")
        return root

    monkeypatch.setattr(BlueFolderAssignments, "_post", fake_post)

    assignments = BlueFolderAssignments().list_for_user_range(13051, "2026.04.16 12:00 AM", "2026.04.16 11:59 PM")

    assert assignments == [
        {
            "assignmentId": "a-1",
            "serviceRequestId": "96268",
            "userIds": ["13051"],
            "comment": "AM stop",
            "start": "2026.04.16 08:00 AM",
            "end": "2026.04.16 10:00 AM",
            "allDay": False,
            "isComplete": True,
            "created": None,
            "completed": None,
            "address": "180 E Hebron Rd",
            "city": "Hebron",
            "state": "ME",
            "zip": "04238",
        }
    ]


def test_assignments_list_for_user_range_validates_inputs():
    assignments = BlueFolderAssignments()

    for kwargs in (
        {"user_id": 0, "start_date": "2026.04.16", "end_date": "2026.04.17"},
        {"user_id": 13051, "start_date": "", "end_date": "2026.04.17"},
        {"user_id": 13051, "start_date": "2026.04.16", "end_date": ""},
        {"user_id": 13051, "start_date": "2026.04.16", "end_date": "2026.04.17", "date_range_type": "updated"},
    ):
        try:
            assignments.list_for_user_range(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {kwargs}")
