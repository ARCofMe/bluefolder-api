# tests/test_users.py

"""Simple construction tests for the users domain client."""

import xml.etree.ElementTree as ET
from bluefolder_api.users import BlueFolderUsers


def test_users_domain():
    u = BlueFolderUsers()
    assert u.domain == "users"


def test_users_get(fake_response):
    u = BlueFolderUsers()

    u.get({"userId": 42})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "get"
    assert xml.find("userId").text == "42"


def test_users_list(fake_response):
    u = BlueFolderUsers()

    u.list({"activeOnly": "true"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("activeOnly").text == "true"

