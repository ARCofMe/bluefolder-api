# tests/test_users.py

"""Tests for the users domain client (list/get/add/edit)."""

import xml.etree.ElementTree as ET
import base64

from bluefolder_api.users import BlueFolderUsers


def test_users_domain():
    u = BlueFolderUsers()
    assert u.domain == "users"


def test_users_get(fake_response):
    u = BlueFolderUsers()

    u.get({"userId": 42})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("userId").text == "42"


def test_users_list(fake_response):
    u = BlueFolderUsers()

    u.list({"activeOnly": "true"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find(".//userList/listType").text == "basic"


# Extended mutation coverage
class DummySession:
    def __init__(self):
        self.calls = []

    def post(self, url, data=None, headers=None, timeout=None):
        self.calls.append({"url": url, "data": data, "headers": headers, "timeout": timeout})

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


def test_user_add_edit_builds_xml():
    users = BlueFolderUsers(client=DummyClient())

    users.add(firstName="Jane", lastName="Doe")
    xml = ET.fromstring(users.session.calls[-1]["data"])
    assert xml.find(".//firstName").text == "Jane"
    assert xml.find(".//lastName").text == "Doe"
    auth = users.session.calls[-1].get("headers", {}).get("Authorization")
    assert auth and base64.b64decode(auth.split(" ", 1)[1]).decode() == "key:x"

    users.edit(user_id=5, firstName="Janet")
    xml = ET.fromstring(users.session.calls[-1]["data"])
    assert xml.find(".//userId").text == "5"
    assert xml.find(".//firstName").text == "Janet"
