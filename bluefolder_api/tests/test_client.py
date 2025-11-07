# tests/test_client.py

from client import BlueFolderClient
from service_requests import BlueFolderServiceRequests

def test_client_inits_all_domains():
    client = BlueFolderClient()
    # sample of a few to ensure construction works
    assert isinstance(client.service_requests, BlueFolderServiceRequests)
    assert hasattr(client, "appointments")
    assert hasattr(client, "users")

def test_client_repr_contains_domains():
    rep = repr(BlueFolderClient())
    assert "BlueFolderClient" in rep
    assert "service_requests" in rep
