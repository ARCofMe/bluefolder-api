"""Mock the upstream transport while exercising the full list facade."""
import logging
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import pytest
from bluefolder_api.client import BlueFolderClient
from bluefolder_api.web_api import create_app


@pytest.mark.parametrize('http_status,xml,expected_status,details', [
    (200, '<response status="fail"><error><code>123</code><message>Invalid date range</message></error></response>', 400, {'code': '123', 'message': 'Invalid date range'}),
    (200, '<response status="ok"><result status="fail"><message>Incomplete response</message></result></response>', 400, {'message': 'Incomplete response'}),
    (400, '<response status="fail"><errorCode>123</errorCode><errorMessage>Invalid date range</errorMessage></response>', 502, {'httpStatus': 400, 'code': '123', 'message': 'Invalid date range'}),
    (400, '<response><error><code>secret-key</code><message>Authorization: Basic secret-auth customer@example.com</message></error></response>', 502, {'httpStatus': 400, 'message': 'Upstream message withheld'}),
    (400, '<html>secret-key secret-auth</html>', 502, {'httpStatus': 400}),
    (400, 'secret-key secret-auth', 502, {'httpStatus': 400}),
    (200, '<response status="fail"/>', 400, {}),
])
def test_safe_errors(monkeypatch, caplog, http_status, xml, expected_status, details):
    caplog.set_level(logging.DEBUG)
    client = BlueFolderClient()
    calls = []
    def post(url, **kwargs):
        calls.append(kwargs)
        return SimpleNamespace(status_code=http_status, content=xml.encode(), text=xml,
                               headers={'Authorization': 'secret-auth'})
    monkeypatch.setattr(client.session, 'post', post)
    response = create_app(lambda: client).test_client().get('/service-requests?startDate=2026-11-06&endDate=2026-11-06')
    assert response.status_code == expected_status
    assert response.json['upstreamError'] == details
    assert len(calls) == 1
    assert any(getattr(record, 'bluefolder_error', None) == details for record in caplog.records)
    exposed = response.get_data(as_text=True) + caplog.text + repr([r.__dict__ for r in caplog.records])
    for secret in ('secret-key', 'secret-auth', 'customer@example.com', 'test-key', 'Authorization'):
        assert secret not in exposed


@pytest.mark.parametrize('start,end', [('01', '05'), ('05', '05'), ('06', '06'), ('06', '07')])
def test_success_and_dates_unchanged(monkeypatch, start, end):
    client = BlueFolderClient()
    calls = []
    xml = '<response status="ok"><serviceRequestList><serviceRequest><id>42</id></serviceRequest></serviceRequestList><filtersApplied><dateRange dateField="dateTimeClosed" wasDefaulted="false"><startDate>start</startDate><endDate>end</endDate></dateRange></filtersApplied></response>'
    def post(url, **kwargs):
        calls.append(kwargs)
        return SimpleNamespace(status_code=200, content=xml.encode(), text=xml, headers={})
    monkeypatch.setattr(client.session, 'post', post)
    response = create_app(lambda: client).test_client().get(f'/service-requests?startDate=2026-11-{start}&endDate=2026-11-{end}&dateField=dateTimeClosed&status=open')
    assert response.status_code == 200
    assert response.json['serviceRequests'][0]['id'] == '42'
    assert response.json['filtersApplied']['wasDefaulted'] is False
    request = ET.fromstring(calls[0]['data']).find('serviceRequestList')
    assert request.findtext('dateRange/startDate') == f'11-{start}-2026 12:00 AM'
    assert request.findtext('dateRange/endDate') == f'11-{end}-2026 11:59 PM'
    assert request.find('dateRange').get('dateField') == 'dateTimeClosed'
    assert request.findtext('status') == 'open'


def test_malformed_success_body_is_sanitized(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    client = BlueFolderClient()
    xml = 'secret-key Authorization secret-auth'
    monkeypatch.setattr(client.session, 'post', lambda *a, **kw: SimpleNamespace(
        status_code=200, content=xml.encode(), text=xml, headers={'Authorization': 'secret-auth'}))
    response = create_app(lambda: client).test_client().get('/service-requests?startDate=2026-11-06&endDate=2026-11-06')
    assert response.status_code == 502
    assert response.json['upstreamError'] == {}
    for secret in ('secret-key', 'secret-auth', 'Authorization'):
        assert secret not in response.get_data(as_text=True) + caplog.text


@pytest.mark.parametrize('content', [b'<!DOCTYPE response [<!ENTITY a "secret">]><response><message>&a;</message></response>', b'x' * 65537])
def test_untrusted_error_body_limits(content):
    from bluefolder_api.diagnostics import response_error_details
    assert response_error_details(SimpleNamespace(content=content)) == {}
