# tests/test_contracts.py

"""Contracts endpoint tests."""

import xml.etree.ElementTree as ET
from bluefolder_api.contracts import BlueFolderContracts


def test_contracts_domain():
    d = BlueFolderContracts()
    assert d.domain == "contracts"


def test_contracts_list(fake_response):
    d = BlueFolderContracts()
    d.list({"serviceRequestId": "200"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("serviceRequestId").text == "200"
