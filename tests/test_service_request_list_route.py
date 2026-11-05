"""Contract tests for the RouteDesk service-request listing facade."""
from bluefolder_api.web_api import create_app


class FakeServiceRequests:
    def __init__(self):
        self.calls = []

    def list_for_range_with_filters(self, **kwargs):
        self.calls.append(kwargs)
        return ([{"id": "103476", "status": "Scheduled", "customerName": "Example"}], {"dateField": "dateTimeCreated", "wasDefaulted": False, "startDate": kwargs["start_date"], "endDate": kwargs["end_date"]})


class FakeClient:
    service_requests = FakeServiceRequests()


def test_list_service_requests_converts_iso_dates_and_returns_array():
    fake = FakeClient()
    response = create_app(lambda: fake).test_client().get(
        "/service-requests?startDate=2026-11-01&endDate=2026-11-05&dateField=dateTimeCreated"
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["serviceRequests"] == [{"id": "103476", "status": "Scheduled", "customerName": "Example"}]
    assert body["filtersApplied"]["wasDefaulted"] is False
    assert fake.service_requests.calls == [{
        "start_date": "11-01-2026 12:00 AM",
        "end_date": "11-05-2026 11:59 PM",
        "date_field": "dateTimeCreated",
        "status": None,
    }]


def test_list_service_requests_passes_status():
    fake = FakeClient()
    response = create_app(lambda: fake).test_client().get(
        "/service-requests?startDate=2026-11-01&endDate=2026-11-02&status=open"
    )
    assert response.status_code == 200
    assert fake.service_requests.calls[0]["status"] == "open"


def test_list_service_requests_rejects_invalid_windows_without_upstream_call():
    fake = FakeClient()
    paths = [
        "/service-requests",
        "/service-requests?startDate=bad&endDate=2026-11-02",
        "/service-requests?startDate=2026-11-05&endDate=2026-11-01",
        "/service-requests?startDate=2026-01-01&endDate=2026-11-01",
        "/service-requests?startDate=2026-11-01&endDate=2026-11-02&dateField=unknown",
    ]
    client = create_app(lambda: fake).test_client()
    for path in paths:
        response = client.get(path)
        assert response.status_code == 400, (path, response.get_json())
    assert fake.service_requests.calls == []
