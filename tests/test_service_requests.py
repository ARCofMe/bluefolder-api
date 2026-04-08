"""Mutation helpers for service requests: add/edit, assignment, comments, labor, materials."""

import xml.etree.ElementTree as ET
import pytest

from bluefolder_api.service_requests import BlueFolderServiceRequests


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


@pytest.fixture
def sr():
    return BlueFolderServiceRequests(client=DummyClient())


def test_add_builds_xml(sr):
    sr.add(description="Test", customerId=1, customFields={"foo": "bar"})
    data = sr.session.calls[-1]["data"]
    xml = ET.fromstring(data)
    assert xml.find(".//description").text == "Test"
    assert xml.find(".//customerId").text == "1"
    assert xml.find(".//customField[@name='foo']").text == "bar"


def test_add_assignment(sr):
    sr.add_assignment(123, [1, 2], start_date="2025.01.01 12:00 AM")
    data = sr.session.calls[-1]["data"]
    xml = ET.fromstring(data)
    assert xml.find(".//serviceRequestId").text == "123"
    assert xml.find(".//serviceRequestAssignmentAdd") is not None
    assignees = [u.text for u in xml.findall(".//assignedTo/userId")]
    assert assignees == ["1", "2"]


def test_edit_assignment(sr):
    sr.edit_assignment(
        456,
        assignmentComment="ETA update",
        assigneeUserIds=[7],
    )
    data = sr.session.calls[-1]["data"]
    xml = ET.fromstring(data)
    assert xml.find(".//serviceRequestAssignmentEdit") is not None
    assert xml.find(".//assignmentId").text == "456"
    assert xml.find(".//assignmentComment").text == "ETA update"
    assignees = [u.text for u in xml.findall(".//assignedTo/userId")]
    assert assignees == ["7"]


def test_complete_assignment(sr):
    sr.complete_assignment(789, comment="done")
    data = sr.session.calls[-1]["data"]
    xml = ET.fromstring(data)
    assert xml.find(".//serviceRequestAssignmentComplete") is not None
    assert xml.find(".//assignmentId").text == "789"
    assert xml.find(".//completionComment").text == "done"


def test_add_comment(sr):
    sr.add_comment(10, "hello", comment_is_public=True, user_id=42)
    data = sr.session.calls[-1]["data"]
    xml = ET.fromstring(data)
    assert xml.find(".//serviceRequestId").text == "10"
    assert xml.find(".//comment").text == "hello"
    assert xml.find(".//userId").text == "42"
    assert xml.find(".//commentIsPublic").text == "true"


def test_list_for_range_includes_status_fields(sr, monkeypatch):
    response = ET.fromstring(
        """
        <response status="ok">
          <serviceRequests>
            <serviceRequest>
              <id>123</id>
              <subject>Test SR</subject>
              <serviceRequestStatus>Need Parts/Schedule</serviceRequestStatus>
              <serviceRequestStatusName>Need Parts/Schedule</serviceRequestStatusName>
              <customerId>456</customerId>
              <assignedTo>
                <userId>9001</userId>
                <userId>9002</userId>
              </assignedTo>
            </serviceRequest>
          </serviceRequests>
        </response>
        """
    )
    monkeypatch.setattr(sr, "_post", lambda action, xml_data=None: response)

    rows = sr.list_for_range("2026.04.01 12:00 AM", "2026.04.08 11:59 PM")

    assert rows == [
        {
            "id": "123",
            "subject": "Test SR",
            "status": "Need Parts/Schedule",
            "statusName": "Need Parts/Schedule",
            "customerId": "456",
            "externalId": None,
            "address": None,
            "city": None,
            "state": None,
            "zip": None,
            "start": None,
            "end": None,
            "userIds": ["9001", "9002"],
        }
    ]
