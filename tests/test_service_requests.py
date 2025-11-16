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
    assignees = [u.text for u in xml.findall(".//assigneeUserIds/userId")]
    assert assignees == ["1", "2"]


def test_add_comment(sr):
    sr.add_comment(10, "hello", comment_is_public=True)
    data = sr.session.calls[-1]["data"]
    xml = ET.fromstring(data)
    assert xml.find(".//serviceRequestId").text == "10"
    assert xml.find(".//comment").text == "hello"
    assert xml.find(".//commentIsPublic").text == "true"
