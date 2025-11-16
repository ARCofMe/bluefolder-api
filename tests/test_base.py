# tests/test_base.py

"""Unit tests covering the shared BlueFolderBase helper."""

import xml.etree.ElementTree as ET
import pytest
from bluefolder_api.base import BlueFolderBase


class DummyDomain(BlueFolderBase):
    """Small concrete subclass used to exercise the base behavior."""

    def __init__(self):
        super().__init__(domain="Dummy")


def test_init_loads_env(monkeypatch):
    """The base class should load credentials from the environment."""
    monkeypatch.setenv("BLUEFOLDER_API_KEY", "abc")
    monkeypatch.setenv("BLUEFOLDER_ACCOUNT_NAME", "acct")
    d = DummyDomain()
    assert d.api_key == "abc"
    assert d.account == "acct"
    assert d.base_url == "https://acct.bluefolder.com/api/2.0"


def test_missing_env_raises(monkeypatch):
    """Missing credentials should trigger a ValueError."""
    monkeypatch.delenv("BLUEFOLDER_API_KEY", raising=False)
    monkeypatch.delenv("BLUEFOLDER_ACCOUNT_NAME", raising=False)
    with pytest.raises(ValueError):
        DummyDomain()


def test_build_xml_request_includes_method_and_key():
    """XML requests should include both method and API key."""
    d = DummyDomain()
    xml_bytes = d._build_xml_request("list", {"foo": "bar"})
    xml = ET.fromstring(xml_bytes)
    assert xml.find("method").text == "list"
    assert xml.find("apikey").text == "test-key"
    assert xml.find("foo").text == "bar"


def test_post_calls_requests(fake_response):
    """_post should hit the underlying requests session with proper XML."""
    d = DummyDomain()
    d._post("list", {"x": "1"})

    assert fake_response.called
    assert fake_response.last_url == (
        "https://testaccount.bluefolder.com/api/2.0/Dummy/list.aspx"
    )

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("x").text == "1"


def test_parse_error_raises(monkeypatch):
    """Invalid XML responses should raise a RuntimeError."""
    d = DummyDomain()

    class BadResp:
        status_code = 200
        content = b"not xml"
        text = "not xml"

    monkeypatch.setattr("bluefolder_api.base.requests.post", lambda *a, **kw: BadResp())
    monkeypatch.setattr(
        "bluefolder_api.base.requests.Session.post", lambda *a, **kw: BadResp()
    )

    with pytest.raises(RuntimeError):
        d._post("list", {"foo": "bar"})
