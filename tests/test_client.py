# tests/test_client.py

import os
import pytest
from bluefolder_api.client import BlueFolderClient

def test_base_url_override(monkeypatch):
    monkeypatch.setenv("BLUEFOLDER_API_KEY", "key")
    monkeypatch.delenv("BLUEFOLDER_ACCOUNT_NAME", raising=False)
    # No account name env needed when it can be inferred from the base URL
    client = BlueFolderClient(base_url="https://custom.bluefolder.com/api/2.0")
    assert client.base_url == "https://custom.bluefolder.com/api/2.0"
    assert client.account == "custom"

def test_env_account_used_when_no_base_url(monkeypatch):
    monkeypatch.setenv("BLUEFOLDER_API_KEY", "key")
    monkeypatch.setenv("BLUEFOLDER_ACCOUNT_NAME", "myacct")
    client = BlueFolderClient()
    assert client.base_url == "https://myacct.bluefolder.com/api/2.0"

def test_missing_account_defaults_to_shared_app_host(monkeypatch):
    monkeypatch.setenv("BLUEFOLDER_API_KEY", "key")
    monkeypatch.delenv("BLUEFOLDER_ACCOUNT_NAME", raising=False)
    monkeypatch.delenv("BLUEFOLDER_BASE_URL", raising=False)
    client = BlueFolderClient()
    assert client.base_url == "https://app.bluefolder.com/api/2.0"
    assert client.account is None

def test_custom_proxy_base_url_no_longer_requires_account(monkeypatch):
    monkeypatch.setenv("BLUEFOLDER_API_KEY", "key")
    monkeypatch.delenv("BLUEFOLDER_ACCOUNT_NAME", raising=False)
    client = BlueFolderClient(base_url="https://20.40.202.18/api/2.0")
    assert client.base_url == "https://20.40.202.18/api/2.0"

def test_client_initializes_domains(monkeypatch):
    """Ensure the client loads all expected domain handlers."""
    monkeypatch.setenv("BLUEFOLDER_API_KEY", "abc")
    monkeypatch.setenv("BLUEFOLDER_ACCOUNT_NAME", "acct")

    c = BlueFolderClient()

    assert hasattr(c, "customers")
    assert hasattr(c, "service_requests")
    assert hasattr(c, "appointments")
    assert hasattr(c, "materials")
    assert hasattr(c, "equipment")
    assert hasattr(c, "users")
    assert hasattr(c, "assignments")
    assert hasattr(c, "attachments")
    assert hasattr(c, "comments")
    assert hasattr(c, "contracts")
    assert hasattr(c, "custom_fields")
    assert hasattr(c, "item_lists")
    assert hasattr(c, "expenses")
    assert hasattr(c, "labor")
    assert hasattr(c, "tax_codes")
