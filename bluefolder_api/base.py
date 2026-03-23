"""Base abstractions shared by the BlueFolder domain clients."""

import os
import logging
import xml.etree.ElementTree as ET
from abc import ABC
import base64

# Retry support is optional so unit tests can run without the requests/urllib3 extras.
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except Exception:  # pragma: no cover - fallback when requests isn't installed
    HTTPAdapter = None
    Retry = None

try:  # optional in test environments
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - test stub

    def load_dotenv(*args, **kwargs):
        return None


try:  # prefer real requests, but allow stubs during tests
    import requests
except ImportError:  # pragma: no cover - test stub

    class _DummyResp:
        status_code = 200
        text = ""
        content = b""
        headers = {}

        def raise_for_status(self):
            return None

    def _dummy_post(url, data=None, headers=None, timeout=None):
        return _DummyResp()

    class _DummySession:
        def __init__(self):
            self.calls = []

        def post(self, url, data=None, headers=None, timeout=None):
            self.calls.append({"url": url, "data": data})
            return _DummyResp()

    requests = type(
        "requests",
        (),
        {
            "Session": _DummySession,
            "post": staticmethod(_dummy_post),
        },
    )

# -----------------------------------------------------------------------------
# Environment Loading
# -----------------------------------------------------------------------------
# Automatically locate and load .env from either an explicit path or project root.
env_path = os.getenv("BLUEFOLDER_ENV_PATH")  # optional override
if not env_path:
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(os.path.dirname(here), ".env")
    env_path = (
        candidate if os.path.exists(candidate) else os.path.join(os.getcwd(), ".env")
    )

load_dotenv(dotenv_path=env_path)

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# -----------------------------------------------------------------------------
# BlueFolderBase
# -----------------------------------------------------------------------------
class BlueFolderBase(ABC):
    """
    Base class for all BlueFolder API domain modules.

    This class provides common authentication, XML request construction,
    and HTTP POST helpers shared across all endpoint domains.

    Each subclass should inherit and pass its domain name, e.g.:

        class BlueFolderUsers(BlueFolderBase):
            def __init__(self, client=None):
                super().__init__(domain="users", client=client)

    Parameters
    ----------
    domain : str
        The logical API domain name (e.g. "users", "appointments").
        Used to automatically construct endpoint URLs.
    client : BlueFolderClient, optional
        Reference to the parent BlueFolderClient instance which provides
        the shared session, base URL, and API key/account context.
    """

    def __init__(
        self,
        domain: str,
        client=None,
        timeout: float | None = 30.0,
        domain_base_url: str | None = None,
        domain_base_env: str | None = None,
        default_base_url: str | None = None,
    ):
        """Capture common configuration for a specific BlueFolder domain."""
        self.domain = domain
        self.client = client
        timeout_env = os.getenv("BLUEFOLDER_TIMEOUT_SECONDS")
        try:
            self.timeout = float(timeout_env) if timeout_env else timeout
        except Exception:
            self.timeout = timeout

        # Load credentials from environment
        self.api_key = os.getenv("BLUEFOLDER_API_KEY")
        self.account = os.getenv("BLUEFOLDER_ACCOUNT_NAME")

        if not self.api_key or not self.account:
            raise ValueError(
                "Missing BLUEFOLDER_API_KEY or BLUEFOLDER_ACCOUNT_NAME in .env"
            )

        # Base API URL can be overridden for custom DNS/routing; otherwise derive from account.
        domain_env_override = os.getenv(domain_base_env) if domain_base_env else None
        override_base = (
            domain_base_url
            or domain_env_override
            or os.getenv("BLUEFOLDER_BASE_URL")
            or default_base_url
            or getattr(client, "base_url", None)
            or f"https://{self.account}.bluefolder.com/api/2.0"
        )
        self.base_url = override_base.rstrip("/")
        self.url = self.base_url

        # Use the shared session if available
        self.session = getattr(client, "session", None) or requests.Session()

        # Optional SSL verification toggle
        verify_env = os.getenv("BLUEFOLDER_VERIFY_SSL")
        if verify_env is not None:
            self.session.verify = str(verify_env).lower() not in ("0", "false", "no")

        # Optional Host header override (useful when BLUEFOLDER_BASE_URL points to an IP)
        self._host_header = os.getenv("BLUEFOLDER_HOST_HEADER")

        # Configure retries on the session
        if HTTPAdapter and Retry:
            try:
                retry_total = int(os.getenv("BLUEFOLDER_RETRY_TOTAL") or 3)
                retry_backoff = float(os.getenv("BLUEFOLDER_RETRY_BACKOFF") or 1)
                retry = Retry(
                    total=retry_total,
                    backoff_factor=retry_backoff,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["POST"],
                    raise_on_status=False,
                )
                adapter = HTTPAdapter(max_retries=retry)
                self.session.mount("https://", adapter)
                self.session.mount("http://", adapter)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # XML request builders and POST handlers
    # -------------------------------------------------------------------------
    def _build_xml_request(self, action: str, params: dict | None = None) -> bytes:
        """
        Build a BlueFolder XML <request> body, including authentication.

        Example:
            <request>
                <apikey>your_key_here</apikey>
                <someParam>someValue</someParam>
            </request>

        Parameters
        ----------
        params : dict, optional
            Additional XML child elements to include in the request.

        Returns
        -------
        bytes
            UTF-8 encoded XML request body.
        """
        root = ET.Element("request")
        ET.SubElement(root, "method").text = action
        ET.SubElement(root, "apikey").text = self.api_key

        if params:
            for key, value in params.items():
                if value is None or value == "":
                    # Skip empty fields to avoid sending "None" or blank tags that fail API validation.
                    continue
                ET.SubElement(root, key).text = str(value)

        return ET.tostring(root, encoding="utf-8", method="xml")

    # -------------------------------------------------------------------------
    def _post(self, action: str, xml_data=None, params=None, override_url: str = None):
        """
        Perform an XML POST to a BlueFolder domain endpoint.

        Constructs a URL like:
            https://{account}.bluefolder.com/api/2.0/{domain}/{action}.aspx

        Parameters
        ----------
        action : str
            The specific endpoint action (e.g., "list", "get", "add").
        xml_data : bytes, optional
            Prebuilt XML request body; if not provided, one is generated from `params`.
        params : dict, optional
            Dictionary of XML parameters if not providing `xml_data`.
        override_url : str, optional
            Custom URL to post to (for edge cases like serviceRequests/getAssignmentList.aspx).

        Returns
        -------
        xml.etree.ElementTree.Element
            Parsed XML response root element.

        Raises
        ------
        RuntimeError
            If response is not valid XML.
        HTTPError
            If a non-200 HTTP status is returned.
        """
        url = override_url or f"{self.base_url.rstrip('/')}/{self.domain}/{action}.aspx"

        if xml_data is None:
            xml_data = self._build_xml_request(action, params)

        # if tests pass a dict → build xml
        if isinstance(xml_data, dict):
            xml_data = self._build_xml_request(action, xml_data)

        # BlueFolder expects authentication in a Basic header
        credentials = f"{self.api_key}:{self.account}"
        token = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Content-Type": "application/xml",
            "Authorization": f"Basic {token}",
        }

        logger.debug(f"POST → {url}\n{xml_data.decode()}")
        hdrs = headers or {}
        if self._host_header:
            hdrs = dict(hdrs)
            hdrs["Host"] = self._host_header

        response = self.session.post(
            url, data=xml_data, headers=hdrs, timeout=self.timeout
        )
        logger.debug(f"Status: {response.status_code}\nResponse:\n{response.text}")

        if response.status_code != 200:
            logger.error(f"Error {response.status_code}: {response.text}")
            response.raise_for_status()

        try:
            return ET.fromstring(response.content)
        except ET.ParseError as e:
            resp_headers = getattr(response, "headers", {}) or {}
            resp_text = getattr(response, "text", "")
            resp_status = getattr(response, "status_code", "n/a")
            log_message = "Invalid XML from %s (status=%s, headers=%s):\n%s"
            log_args = (url, resp_status, dict(resp_headers), resp_text)
            if not str(resp_text).strip():
                logger.warning(*((log_message,) + log_args))
            else:
                logger.error(*((log_message,) + log_args))
            raise RuntimeError("Invalid XML response") from e

    # -------------------------------------------------------------------------
    def _post_raw(self, endpoint: str, xml_body: str):
        """
        Perform a direct XML POST against a fully-qualified endpoint.
        This bypasses `_build_xml_request` entirely and is used for
        custom endpoints (e.g. users/list.aspx).

        Parameters
        ----------
        endpoint : str
            The endpoint relative to the base URL (e.g. "users/list.aspx").
        xml_body : str
            Fully-formed XML request body string.

        Returns
        -------
        str
            Raw response text.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {"Content-Type": "application/xml"}
        logger.debug(f"POST → {url}\n{xml_body}")

        response = self.session.post(
            url, data=xml_body.encode("utf-8"), headers=headers
        )
        response.raise_for_status()
        return response.text

    # -------------------------------------------------------------------------
    # Common CRUD-style operations
    # -------------------------------------------------------------------------
    def get(self, params: dict = None):
        """Perform a standard `get` operation."""
        return self._post("get", params=params)

    def list(self, params: dict = None):
        """Perform a standard `list` operation."""
        return self._post("list", params=params)

    def create(self, params: dict):
        """Perform a standard `add` (create) operation."""
        return self._post("add", params=params)

    def update(self, params: dict):
        """Perform a standard `edit` (update) operation."""
        return self._post("edit", params=params)

    # Uncomment if your API supports deletes:
    # def delete(self, params: dict):
    #     """Perform a standard `delete` operation."""
    #     return self._post("delete", params=params)
