# tests/test_service_requests.py

import xml.etree.ElementTree as ET
from service_requests import BlueFolderServiceRequests

def test_service_requests_inherits_domain(fake_response):
    sr = BlueFolderServiceRequests()
    assert sr.domain == "ServiceRequests"

def test_list_uses_correct_method(fake_response):
    sr = BlueFolderServiceRequests()
    sr.list({"id": 123})
    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("apikey").text == "test-key"
    assert xml.find("id").text == "123"
