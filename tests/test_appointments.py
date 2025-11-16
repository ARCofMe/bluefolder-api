# tests/test_appointments.py

"""Sanity checks for the appointments domain client."""

import xml.etree.ElementTree as ET
from bluefolder_api.appointments import BlueFolderAppointments


def test_appointments_domain():
    a = BlueFolderAppointments()
    assert a.domain == "appointments"


def test_appointments_list(fake_response):
    a = BlueFolderAppointments()
    a.list({"userId": "7"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("userId").text == "7"


def test_appointments_get(fake_response):
    a = BlueFolderAppointments()
    a.get({"id": "22"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "get"
    assert xml.find("id").text == "22"

