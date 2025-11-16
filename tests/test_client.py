# tests/test_client.py

import pytest
from bluefolder_api.client import BlueFolderClient


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

