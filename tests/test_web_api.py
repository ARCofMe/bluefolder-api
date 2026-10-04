from bluefolder_api.web_api import create_app


class FakeAssignments:
    def list_for_user_range(self, user_id, start_date, end_date, date_range_type="scheduled"):
        return [{
            "assignmentId": "A1",
            "serviceRequestId": "SR1",
            "userIds": [str(user_id)],
            "start": start_date,
            "end": end_date,
            "allDay": False,
            "isComplete": False,
        }]


class FakeServiceRequests:
    def get_by_id(self, service_request_id):
        import xml.etree.ElementTree as ET
        return ET.fromstring("""<response><serviceRequest>
          <id>102052</id><subject>Test repair</subject>
          <serviceRequestStatus>Open</serviceRequestStatus>
          <customerId>123</customerId>
          <locationAddress>9 Example Rd</locationAddress>
          <locationCity>Hebron</locationCity><locationState>ME</locationState>
          <locationZip>04238</locationZip>
        </serviceRequest></response>""")

    _parse_service_request = staticmethod(__import__("bluefolder_api.service_requests", fromlist=["BlueFolderServiceRequests"]).BlueFolderServiceRequests._parse_service_request)


class FakeUsers:
    def list_all(self):
        return [{"userId": "33538043", "displayName": "David Durost", "inactive": False}]

    def list_active(self):
        return self.list_all()


class FakeClient:
    def __init__(self):
        self.assignments = FakeAssignments()
        self.users = FakeUsers()
        self.service_requests = FakeServiceRequests()


def test_assignments_by_iso_date():
    client = create_app(FakeClient).test_client()
    response = client.get("/assignments?userId=33538043&date=2026-10-03")
    assert response.status_code == 200
    body = response.get_json()
    assert body["startDate"] == "2026.10.03 12:00 AM"
    assert body["endDate"] == "2026.10.03 11:59 PM"
    assert body["assignments"][0]["serviceRequestId"] == "SR1"


def test_assignments_requires_user():
    client = create_app(FakeClient).test_client()
    response = client.get("/assignments?date=2026-10-03")
    assert response.status_code == 400


def test_users():
    client = create_app(FakeClient).test_client()
    response = client.get("/users")
    assert response.status_code == 200
    assert response.get_json()["users"][0]["userId"] == "33538043"


def test_service_request_by_id():
    client = create_app(FakeClient).test_client()
    response = client.get("/service-requests/102052")
    assert response.status_code == 200
    body = response.get_json()["serviceRequest"]
    assert body["id"] == "102052"
    assert body["formattedAddress"] == "9 Example Rd, Hebron ME 04238"
