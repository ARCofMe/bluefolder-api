# tests/test_comments.py

"""Comments endpoint tests."""

import xml.etree.ElementTree as ET
import pytest

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


def test_comments_list_for_service_request_parses_visibility(monkeypatch):
    root = ET.Element("response")
    comment = ET.SubElement(root, "comment")
    ET.SubElement(comment, "id").text = "1"
    ET.SubElement(comment, "userName").text = "Dispatcher"
    ET.SubElement(comment, "dateCreated").text = "2026.04.16 08:00 AM"
    ET.SubElement(comment, "commentText").text = "Call ahead completed"
    ET.SubElement(comment, "isVisibleToCustomer").text = "true"
    client = BlueFolderComments()
    monkeypatch.setattr(client, "_post", lambda *args, **kwargs: root)

    assert client.list_for_service_request(96268) == [
        {
            "id": "1",
            "author": "Dispatcher",
            "dateCreated": "2026.04.16 08:00 AM",
            "text": "Call ahead completed",
            "isVisibleToCustomer": True,
        }
    ]


def test_comments_validate_id_and_text():
    client = BlueFolderComments()

    with pytest.raises(ValueError):
        client.list_for_service_request(0)
    with pytest.raises(ValueError):
        client.add_to_service_request(96268, " ")
    with pytest.raises(ValueError):
        client.add_to_service_request("", "valid")
