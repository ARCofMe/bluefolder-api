import xml.etree.ElementTree as ET
import pytest

from bluefolder_api.customer_contacts import BlueFolderCustomerContacts
from bluefolder_api.customer_locations import BlueFolderCustomerLocations


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


def test_contact_add_edit_delete_xml():
    contacts = BlueFolderCustomerContacts(client=DummyClient())
    contacts.add(customer_id=1, firstName="Jane")
    xml = ET.fromstring(contacts.session.calls[-1]["data"])
    assert xml.find(".//customerId").text == "1"
    assert xml.find(".//firstName").text == "Jane"

    contacts.edit(contact_id=10, firstName="Janet")
    xml = ET.fromstring(contacts.session.calls[-1]["data"])
    assert xml.find(".//customerContactId").text == "10"
    assert xml.find(".//firstName").text == "Janet"

    contacts.delete(contact_id=11)
    xml = ET.fromstring(contacts.session.calls[-1]["data"])
    assert xml.find(".//id").text == "11"


def test_location_add_edit_delete_xml():
    locations = BlueFolderCustomerLocations(client=DummyClient())
    locations.add(customer_id=2, locationName="HQ")
    xml = ET.fromstring(locations.session.calls[-1]["data"])
    assert xml.find(".//customerId").text == "2"
    assert xml.find(".//locationName").text == "HQ"

    locations.edit(location_id=20, locationName="Warehouse")
    xml = ET.fromstring(locations.session.calls[-1]["data"])
    assert xml.find(".//customerLocationId").text == "20"
    assert xml.find(".//locationName").text == "Warehouse"

    locations.delete(location_id=21)
    xml = ET.fromstring(locations.session.calls[-1]["data"])
    assert xml.find(".//customerLocationId").text == "21"


def test_contact_reads_return_empty_when_endpoint_is_unsupported(monkeypatch):
    contacts = BlueFolderCustomerContacts(client=DummyClient())

    def raise_not_found(*args, **kwargs):
        raise RuntimeError("404 Client Error: Not Found for url: https://example.bluefolder.com/api/2.0/customers/get.aspx")

    monkeypatch.setattr(contacts, "_customer_get_fallback", raise_not_found)

    assert contacts.list_for_customer(1) == []


def test_contact_get_uses_documented_customers_endpoint():
    contacts = BlueFolderCustomerContacts(client=DummyClient())
    contacts.get_by_id(10)
    assert contacts.session.calls[-1]["url"].endswith("/customers/getContact.aspx")


def test_contact_get_skips_repeated_calls_after_missing_endpoint(monkeypatch):
    contacts = BlueFolderCustomerContacts(client=DummyClient())

    def raise_not_found(*args, **kwargs):
        raise RuntimeError("404 Client Error: Not Found for url: https://example.bluefolder.com/api/2.0/customers/getContact.aspx")

    monkeypatch.setattr(contacts, "_post", raise_not_found)

    assert contacts.get_by_id(10) == {}
    assert contacts.get_by_id(10) == {}
