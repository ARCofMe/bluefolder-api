# tests/conftest.py

import pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    """Provide dummy env vars for all tests."""
    monkeypatch.setenv("BLUEFOLDER_API_KEY", "test-key")
    monkeypatch.setenv("BLUEFOLDER_ACCOUNT_NAME", "testaccount")

@pytest.fixture
def fake_response(monkeypatch):
    """Monkeypatch requests.post to avoid network calls."""
    import types

    class FakeResponse:
        status_code = 200
        content = b"<response status='ok'><result>success</result></response>"
        text = content.decode()

    def fake_post(url, data=None, headers=None):
        fake_post.called = True
        fake_post.last_url = url
        fake_post.last_data = data
        fake_post.last_headers = headers
        return FakeResponse()

    monkeypatch.setattr("requests.post", fake_post)
    return fake_post
