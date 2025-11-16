# tests/test_tax_codes.py

""" TaxCodes endpoint tests. """

import xml.etree.ElementTree as ET
from bluefolder_api.tax_codes import BlueFolderTaxCodes


def test_tax_codes_domain():
    d = BlueFolderTaxCodes()
    assert d.domain == "taxCodes"


def test_tax_codes_list(fake_response):
    d = BlueFolderTaxCodes()
    d.list({"serviceRequestId": "200"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("serviceRequestId").text == "200"
