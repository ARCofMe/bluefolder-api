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
    """Monkeypatch requests.post AND requests.Session.post to avoid network calls."""
    class FakeResponse:
        status_code = 200
        content = b"<response status='ok'><result>success</result></response>"
        text = content.decode()

    def fake_post(*args, **kwargs):
        """
        Handles both:
            requests.post(url, data=..., headers=...)
        and:
            session.post(url, data=..., headers=...)
        """
        # Positional pattern:
        #   if called as requests.post(url,...)
        #   → args = (url,)
        #
        #   if called as session.post(url,...)
        #   → args = (session_instance, url)
        if len(args) == 1:
            url = args[0]
        else:
            url = args[1]  # skip "self"

        data = kwargs.get("data")
        headers = kwargs.get("headers")

        fake_post.called = True
        fake_post.last_url = url
        fake_post.last_data = data
        fake_post.last_headers = headers

        return FakeResponse()

    # Patch BOTH call types
    monkeypatch.setattr("bluefolder_api.base.requests.post", fake_post)
    monkeypatch.setattr("bluefolder_api.base.requests.Session.post", fake_post)

    return fake_post
