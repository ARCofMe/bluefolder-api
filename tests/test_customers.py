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


# Mutation coverage
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


def test_customer_add_edit_delete_builds_xml():
    cust = BlueFolderCustomers(client=DummyClient())
    cust.add(name="ACME", externalId="X1")
    xml = ET.fromstring(cust.session.calls[-1]["data"])
    assert xml.find(".//name").text == "ACME"
    assert xml.find(".//externalId").text == "X1"

    cust.edit(customer_id=5, name="New Name")
    xml = ET.fromstring(cust.session.calls[-1]["data"])
    assert xml.find(".//customerId").text == "5"
    assert xml.find(".//name").text == "New Name"

    cust.delete(customer_id=6)
    xml = ET.fromstring(cust.session.calls[-1]["data"])
    assert xml.find(".//customerId").text == "6"
