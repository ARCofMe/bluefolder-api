import os
import sys
from pathlib import Path
import types

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Provide lightweight stubs for external deps if not installed
if "requests" not in sys.modules:

    class DummyResp:
        status_code = 200
        content = b"<response status='ok'></response>"
        text = "<response status='ok'></response>"

    class DummySession:
        def __init__(self):
            self.calls = []

        def post(self, url, data=None, headers=None, timeout=None):
            self.calls.append({"url": url, "data": data})
            return DummyResp()

    def _dummy_post(url, data=None, headers=None, timeout=None):
        return DummyResp()

    requests = types.SimpleNamespace(Session=DummySession, post=_dummy_post)
    sys.modules["requests"] = requests

if "dotenv" not in sys.modules:
    sys.modules["dotenv"] = types.SimpleNamespace(
        load_dotenv=lambda *args, **kwargs: None
    )

# Ensure base module-level env lookups succeed
os.environ.setdefault("BLUEFOLDER_API_KEY", "test-key")
os.environ.setdefault("BLUEFOLDER_ACCOUNT_NAME", "testaccount")


import pytest


@pytest.fixture
def fake_response(monkeypatch):
    """Monkeypatch requests.post AND requests.Session.post to avoid network calls."""

    class FakeResponse:
        status_code = 200
        content = b"<response status='ok'><result>success</result></response>"
        text = content.decode()

    def fake_post(*args, **kwargs):
        # Supports both requests.post(url, ...) and session.post(self, url,...)
        url = args[0] if len(args) == 1 else args[1]
        data = kwargs.get("data")
        headers = kwargs.get("headers")
        fake_post.called = True
        fake_post.last_url = url
        fake_post.last_data = data
        fake_post.last_headers = headers
        return FakeResponse()

    monkeypatch.setattr("bluefolder_api.base.requests.post", fake_post)
    monkeypatch.setattr("bluefolder_api.base.requests.Session.post", fake_post)

    return fake_post
