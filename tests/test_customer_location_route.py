"""Read-only connector contract using the real SDK and a fake upstream session."""
import xml.etree.ElementTree as ET
from types import SimpleNamespace

import pytest

from bluefolder_api.customer_locations import BlueFolderCustomerLocations
from bluefolder_api.exceptions import BlueFolderRequestError
from bluefolder_api.web_api import create_app


LOCATION_XML = b'''<response status="ok"><customerLocation>
<customerLocationId>456</customerLocationId><customerId>123</customerId>
<addressStreet>123 Example Street</addressStreet><addressCity>Rockland</addressCity>
<addressState>ME</addressState><addressPostalCode>04841</addressPostalCode>
<addressCountry>United States</addressCountry><isPrimary>true</isPrimary>
<locationName>Test Unit 2</locationName><locationNotes>Test only</locationNotes>
<phone>207-555-0100</phone><primaryContactId>88</primaryContactId>
<serviceManagerId>99</serviceManagerId><technicianId>100</technicianId>
<zone>  Midcoast / Friday  </zone>
</customerLocation></response>'''


class Session:
    def __init__(self, payload=LOCATION_XML):
        self.payload = payload
        self.calls = []

    def post(self, url, data=None, headers=None, timeout=None):
        self.calls.append((url, data))
        return SimpleNamespace(status_code=200, content=self.payload,
                               text=self.payload.decode(), headers={})


def sdk(session):
    client = SimpleNamespace(base_url="https://example.bluefolder.com/api/2.0",
                             api_key="test-key", account="example", session=session)
    return BlueFolderCustomerLocations(client=client)


def test_official_location_get_contract(monkeypatch):
    monkeypatch.delenv("BLUEFOLDER_BASE_URL", raising=False)
    session = Session()
    location = sdk(session).get_location(456)
    url, data = session.calls[0]
    assert url == "https://example.bluefolder.com/api/2.0/customers/getLocation.aspx"
    request = ET.fromstring(data)
    assert request.tag == "request"
    assert [node.tag for node in request] == ["customerLocationGet"]
    assert [node.tag for node in request[0]] == ["customerLocationId"]
    assert request[0][0].text == "456"
    assert location == {
        "id": "456", "customerId": "123", "name": "Test Unit 2", "isPrimary": True,
        "address": "123 Example Street", "city": "Rockland", "state": "ME",
        "zip": "04841", "country": "United States",
        "formattedAddress": "123 Example Street, Rockland ME 04841",
        "notes": "Test only", "zone": "  Midcoast / Friday  ",
        "phone": "207-555-0100", "primaryContactId": "88",
        "serviceManagerId": "99", "technicianId": "100",
    }


def test_route_success_uses_sdk_and_preserves_raw_zone(monkeypatch):
    monkeypatch.delenv("ARCOM_WRAPPER_API_KEY", raising=False)
    session = Session()
    client = create_app(lambda: SimpleNamespace(customer_locations=sdk(session))).test_client()
    response = client.get("/customer-locations/456")
    assert response.status_code == 200
    assert response.get_json()["customerLocation"]["zone"] == "  Midcoast / Friday  "
    assert response.get_json()["customerLocation"]["id"] == "456"
    assert len(session.calls) == 1


@pytest.mark.parametrize("value", ["0", "-1", "abc", "1.5", "１２"])
def test_invalid_ids_do_not_call_upstream(monkeypatch, value):
    monkeypatch.delenv("ARCOM_WRAPPER_API_KEY", raising=False)
    def factory():
        pytest.fail("invalid location ID must not construct an upstream client")
    assert create_app(factory).test_client().get("/customer-locations/" + value).status_code == 400


@pytest.mark.parametrize("payload,status", [
    (b'<response status="ok"/>', 404),
    (b'<response status="error"><error>private detail</error></response>', 502),
    (LOCATION_XML.replace(b'<customerLocationId>456', b'<customerLocationId>999'), 502),
    (b'<response status="ok"><customerLocation/></response>', 502),
])
def test_absent_rejected_or_mismatched_location(monkeypatch, payload, status):
    monkeypatch.delenv("ARCOM_WRAPPER_API_KEY", raising=False)
    session = Session(payload)
    client = create_app(lambda: SimpleNamespace(customer_locations=sdk(session))).test_client()
    response = client.get("/customer-locations/456")
    assert response.status_code == status
    assert "private detail" not in response.get_data(as_text=True)


def test_blank_optional_fields(monkeypatch):
    monkeypatch.delenv("ARCOM_WRAPPER_API_KEY", raising=False)
    session = Session(b'<response status="ok"><customerLocation><customerLocationId>456</customerLocationId></customerLocation></response>')
    location = sdk(session).get_location(456)
    assert location["zone"] == ""
    assert location["country"] == ""
    assert location["phone"] == ""
    assert location["primaryContactId"] is None
    assert location["isPrimary"] is False


def test_upstream_error_is_not_reported_as_not_found(monkeypatch):
    monkeypatch.delenv("ARCOM_WRAPPER_API_KEY", raising=False)
    class FailingLocations:
        def get_location(self, location_id):
            raise BlueFolderRequestError("private upstream detail")
    response = create_app(lambda: SimpleNamespace(customer_locations=FailingLocations())).test_client().get("/customer-locations/456")
    assert response.status_code == 502
    assert "private upstream detail" not in response.get_data(as_text=True)


def test_route_uses_existing_wrapper_key(monkeypatch):
    monkeypatch.setenv("ARCOM_WRAPPER_API_KEY", "test-wrapper-key")
    session = Session()
    client = create_app(lambda: SimpleNamespace(customer_locations=sdk(session))).test_client()
    assert client.get("/customer-locations/456").status_code == 401
    assert session.calls == []
    assert client.get("/customer-locations/456", headers={"X-ARCOM-API-Key": "wrong"}).status_code == 401
    assert client.get("/customer-locations/456", headers={"X-ARCOM-API-Key": "test-wrapper-key"}).status_code == 200
