# tests/test_appointments.py

"""Sanity and mutation checks for the appointments domain client."""

import xml.etree.ElementTree as ET
from bluefolder_api.appointments import BlueFolderAppointments


def test_appointments_domain():
    a = BlueFolderAppointments()
    assert a.domain == "appointments"


def test_appointments_list(fake_response):
    a = BlueFolderAppointments()
    a.list({"userId": "7"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method") is None
    assert xml.find("userId").text == "7"


def test_appointments_get(fake_response):
    a = BlueFolderAppointments()
    a.get({"id": "22"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method") is None
    assert xml.find(".//appointmentGet/apptId").text == "22"


def test_appointments_add_edit_builds_xml():
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

    a = BlueFolderAppointments(client=DummyClient())
    a.add(serviceRequestId=5, userId=1, description="Visit")
    xml = ET.fromstring(a.session.calls[-1]["data"])
    assert xml.find(".//serviceRequestId").text == "5"
    assert xml.find(".//description").text == "Visit"

    a.edit(appointment_id=9, description="Changed")
    xml = ET.fromstring(a.session.calls[-1]["data"])
    assert xml.find(".//appointmentId").text == "9"
    assert xml.find(".//description").text == "Changed"
