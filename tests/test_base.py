# tests/test_base.py

import xml.etree.ElementTree as ET
import pytest
from base import BlueFolderBase

class DummyDomain(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Dummy")

def test_init_loads_env(monkeypatch):
    monkeypatch.setenv("BLUEFOLDER_API_KEY", "abc")
    monkeypatch.setenv("BLUEFOLDER_ACCOUNT_NAME", "acct")
    d = DummyDomain()
    assert d.api_key == "abc"
    assert d.account == "acct"
    assert "acct.bluefolder.com" in d.url

def test_missing_env_raises(monkeypatch):
    monkeypatch.delenv("BLUEFOLDER_API_KEY", raising=False)
    monkeypatch.delenv("BLUEFOLDER_ACCOUNT_NAME", raising=False)
    with pytest.raises(ValueError):
        DummyDomain()

def test_build_xml_request_includes_method_and_key():
    d = DummyDomain()
    xml_bytes = d._build_xml_request("list", {"foo": "bar"})
    xml = ET.fromstring(xml_bytes)
    assert xml.find("method").text == "list"
    assert xml.find("apikey").text == "test-key"
    assert xml.find("foo").text == "bar"

def test_post_calls_requests(fake_response):
    d = DummyDomain()
    d._post("list", {"x": "1"})
    assert fake_response.called
    assert fake_response.last_url.endswith("/api/2.0/xml")
    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"

def test_parse_error_raises(monkeypatch):
    d = DummyDomain()
    class BadResp:
        status_code = 200
        content = b"not xml"
        text = "not xml"
    monkeypatch.setattr("requests.post", lambda *a, **kw: BadResp())
    with pytest.raises(RuntimeError):
        d._post("list", {})
