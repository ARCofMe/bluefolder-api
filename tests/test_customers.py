# tests/test_customers.py

"""Sanity tests for the customers domain client."""

import xml.etree.ElementTree as ET
from bluefolder_api.customers import BlueFolderCustomers


def test_customers_domain():
    c = BlueFolderCustomers()
    assert c.domain == "customers"


def test_customers_list(fake_response):
    c = BlueFolderCustomers()
    c.list({"status": "active"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("status").text == "active"


def test_customers_get(fake_response):
    c = BlueFolderCustomers()
    c.get({"customerId": 99})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "get"
    assert xml.find("customerId").text == "99"
