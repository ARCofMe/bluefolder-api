# tests/test_service_requests.py

""" Service Requests endpoint tests. """

import xml.etree.ElementTree as ET
from bluefolder_api.service_requests import BlueFolderServiceRequests


def test_service_requests_inherits_domain():
    sr = BlueFolderServiceRequests()
    assert sr.domain == "serviceRequests"


def test_list_uses_correct_method(fake_response):
    sr = BlueFolderServiceRequests()
    
    sr.list({"id": 123})
    
    assert fake_response.called
    assert fake_response.last_url.endswith("/serviceRequests/list.aspx")

    root = ET.fromstring(fake_response.last_data)
    assert root.find("method").text == "list"
    assert root.find("id").text == "123"
