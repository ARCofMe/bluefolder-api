"""Base abstractions shared by the BlueFolder domain clients."""

import itertools
import os
import logging
import xml.etree.ElementTree as ET
from abc import ABC
import base64
import time
from urllib.parse import urlparse

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
_REQUEST_COUNTER = itertools.count(1)

DEFAULT_BASE_URL = "https://app.bluefolder.com/api/2.0"


def _infer_account_from_base_url(base_url: str | None) -> str | None:
    """Best-effort account-name inference from a standard BlueFolder host URL."""
    if not base_url:
        return None
    hostname = (urlparse(base_url).hostname or "").strip().lower()
    if not hostname.endswith(".bluefolder.com"):
        return None
    prefix = hostname[: -len(".bluefolder.com")].strip(".")
    if not prefix or prefix == "api":
        return None
    return prefix.split(".")[0] or None


def _build_default_base_url(account: str | None) -> str:
    """Return the docs-aligned default API root for this client."""
    if account:
        return f"https://{account}.bluefolder.com/api/2.0"
    return DEFAULT_BASE_URL


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
        use_global_base_url: bool = True,
        use_host_header: bool = True,
    ):
        """Capture common configuration for a specific BlueFolder domain."""
        self.domain = domain
        self.client = client
        timeout_env = os.getenv("BLUEFOLDER_TIMEOUT_SECONDS")
        try:
            self.timeout = float(timeout_env) if timeout_env else timeout
        except Exception:
            self.timeout = timeout

        # Base API URL can be overridden for custom DNS/routing; otherwise derive from account.
        domain_env_override = os.getenv(domain_base_env) if domain_base_env else None
        global_base_url = os.getenv("BLUEFOLDER_BASE_URL") if use_global_base_url else None
        override_base = (
            domain_base_url
            or domain_env_override
            or global_base_url
            or default_base_url
            or getattr(client, "base_url", None)
        )
        # Load credentials from client context first, then environment, then host inference.
        self.api_key = getattr(client, "api_key", None) or os.getenv("BLUEFOLDER_API_KEY")
        self.account = (
            getattr(client, "account", None)
            or os.getenv("BLUEFOLDER_ACCOUNT_NAME")
            or _infer_account_from_base_url(override_base)
        )

        if not self.api_key:
            raise ValueError("Missing BLUEFOLDER_API_KEY in client context or environment")

        if not override_base:
            override_base = _build_default_base_url(self.account)
        self.base_url = override_base.rstrip("/")
        self.url = self.base_url

        # Use the shared session if available
        self.session = getattr(client, "session", None) or requests.Session()
        if not hasattr(self.session, "headers") or getattr(self.session, "headers", None) is None:
            self.session.headers = {}
        self.session.headers.update(
            {
                "Accept": "application/xml, text/xml;q=0.9, */*;q=0.1",
                "User-Agent": os.getenv("BLUEFOLDER_USER_AGENT") or "bluefolder-api/0.1",
            }
        )

        # Optional SSL verification toggle
        verify_env = os.getenv("BLUEFOLDER_VERIFY_SSL")
        if verify_env is not None:
            self.session.verify = str(verify_env).lower() not in ("0", "false", "no")

        # Optional Host header override (useful when BLUEFOLDER_BASE_URL points to an IP)
        self._host_header = os.getenv("BLUEFOLDER_HOST_HEADER") if use_host_header else None

        # Configure retries on the session
        if HTTPAdapter and Retry:
            try:
                retry_total = int(os.getenv("BLUEFOLDER_RETRY_TOTAL") or 3)
                retry_backoff = float(os.getenv("BLUEFOLDER_RETRY_BACKOFF") or 1)
                pool_connections = int(os.getenv("BLUEFOLDER_POOL_CONNECTIONS") or 20)
                pool_maxsize = int(os.getenv("BLUEFOLDER_POOL_MAXSIZE") or 20)
                retry = Retry(
                    total=retry_total,
                    connect=retry_total,
                    read=retry_total,
                    status=0,
                    backoff_factor=retry_backoff,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["POST"],
                    raise_on_status=False,
                    respect_retry_after_header=True,
                )
                adapter = HTTPAdapter(
                    max_retries=retry,
                    pool_connections=pool_connections,
                    pool_maxsize=pool_maxsize,
                )
                self.session.mount("https://", adapter)
                self.session.mount("http://", adapter)
            except Exception:
                pass

    def _auth_headers(self, *, content_type: str = "application/xml") -> dict[str, str]:
        """Build the standard BlueFolder request headers for this client."""
        basic_auth_password = os.getenv("BLUEFOLDER_BASIC_AUTH_PASSWORD", "x")
        credentials = f"{self.api_key}:{basic_auth_password}"
        token = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Content-Type": content_type,
            "Authorization": f"Basic {token}",
        }
        if self._host_header:
            headers["Host"] = self._host_header
        return headers

    def _capability_cache(self) -> dict[str, bool]:
        """Return a shared per-client capability cache."""
        cache = getattr(self.client, "_capability_cache", None)
        if cache is None:
            cache = {}
            if self.client is not None:
                self.client._capability_cache = cache
            else:
                self._capability_cache_local = getattr(self, "_capability_cache_local", {})
                cache = self._capability_cache_local
        return cache

    def _mark_endpoint_unavailable(self, capability: str) -> None:
        self._capability_cache()[capability] = False

    def _endpoint_is_unavailable(self, capability: str) -> bool:
        return self._capability_cache().get(capability) is False

    def _legacy_generic_helpers_disabled(self) -> bool:
        return os.getenv("BLUEFOLDER_DISABLE_GENERIC_HELPERS", "").lower() in {"1", "true", "yes"}

    def _warn_or_block_generic_helper(self, helper_name: str) -> None:
        if self._legacy_generic_helpers_disabled():
            raise NotImplementedError(
                f"{self.__class__.__name__}.{helper_name}() uses the legacy generic request builder. "
                "Override it with a documented request shape or unset BLUEFOLDER_DISABLE_GENERIC_HELPERS."
            )
        logger.warning(
            "%s.%s() is using the legacy generic BlueFolder request helper. "
            "Prefer a domain-specific wrapper payload.",
            self.__class__.__name__,
            helper_name,
        )

    def _is_retryable_action(self, action: str) -> bool:
        normalized = (action or "").lower()
        mutating = any(token in normalized for token in ("add", "edit", "delete", "complete"))
        if not mutating:
            return True
        return os.getenv("BLUEFOLDER_RETRY_MUTATIONS", "").lower() in {"1", "true", "yes"}

    @staticmethod
    def _response_snippet(response) -> str:
        text = getattr(response, "text", None)
        if text is None:
            content = getattr(response, "content", b"")
            if isinstance(content, bytes):
                text = content[:500].decode("utf-8", errors="replace")
            else:
                text = str(content)
        return str(text).strip()[:500]

    def _build_request_url(self, action: str, override_url: str | None = None) -> str:
        return override_url or f"{self.base_url.rstrip('/')}/{self.domain}/{action}.aspx"

    def _coerce_xml_payload(self, action: str, xml_data=None, params=None):
        if xml_data is None:
            xml_data = self._build_xml_request(action, params)
        if isinstance(xml_data, dict):
            xml_data = self._build_xml_request(action, xml_data)
        return xml_data

    def _raise_http_error(self, response, url: str):
        from .exceptions import (
            BlueFolderAuthError,
            BlueFolderNotFoundError,
            BlueFolderRateLimitError,
            BlueFolderRequestError,
            BlueFolderUnsupportedEndpointError,
        )

        status = getattr(response, "status_code", None)
        snippet = self._response_snippet(response)
        message = f"BlueFolder HTTP {status} for {url}: {snippet}".strip()
        if status in (401, 403):
            raise BlueFolderAuthError(message, status_code=status, url=url)
        if status == 404:
            if url.endswith(".aspx"):
                raise BlueFolderUnsupportedEndpointError(message, status_code=status, url=url)
            raise BlueFolderNotFoundError(message, status_code=status, url=url)
        if status == 429:
            retry_after = None
            headers = getattr(response, "headers", {}) or {}
            try:
                retry_after = float(headers.get("Retry-After")) if headers.get("Retry-After") else None
            except Exception:
                retry_after = None
            raise BlueFolderRateLimitError(
                message,
                status_code=status,
                url=url,
                retry_after=retry_after,
            )
        raise BlueFolderRequestError(message, status_code=status, url=url)

    def _perform_request(self, url: str, payload, headers: dict[str, str], action: str):
        request_id = next(_REQUEST_COUNTER)
        retry_total = int(os.getenv("BLUEFOLDER_RETRY_TOTAL") or 3)
        retry_backoff = float(os.getenv("BLUEFOLDER_RETRY_BACKOFF") or 1)
        attempts = retry_total + 1 if self._is_retryable_action(action) else 1
        last_response = None

        for attempt in range(1, attempts + 1):
            payload_preview = payload.decode() if isinstance(payload, (bytes, bytearray)) else str(payload)
            logger.debug(
                "BlueFolder request id=%s attempt=%s action=%s url=%s payload=%s",
                request_id,
                attempt,
                action,
                url,
                payload_preview,
            )
            started = time.monotonic()
            response = self.session.post(
                url,
                data=payload,
                headers=headers,
                timeout=self.timeout,
            )
            try:
                self.session.last_response_headers = dict(getattr(response, "headers", {}) or {})
            except Exception:
                self.session.last_response_headers = {}
            elapsed_ms = int((time.monotonic() - started) * 1000)
            last_response = response
            logger.debug(
                "BlueFolder response id=%s status=%s duration_ms=%s body=%s",
                request_id,
                getattr(response, "status_code", "n/a"),
                elapsed_ms,
                self._response_snippet(response),
            )
            if getattr(response, "status_code", None) == 200:
                return response

            should_retry = (
                attempt < attempts
                and getattr(response, "status_code", None) in {429, 500, 502, 503, 504}
            )
            if should_retry:
                retry_after = None
                headers_in = getattr(response, "headers", {}) or {}
                try:
                    retry_after = float(headers_in.get("Retry-After")) if headers_in.get("Retry-After") else None
                except Exception:
                    retry_after = None
                sleep_for = retry_after if retry_after is not None else retry_backoff * attempt
                logger.warning(
                    "BlueFolder transient HTTP %s for %s, retrying in %.2fs (%s/%s).",
                    getattr(response, "status_code", "n/a"),
                    url,
                    sleep_for,
                    attempt,
                    attempts - 1,
                )
                time.sleep(sleep_for)
                continue

            logger.error("Error %s: %s", getattr(response, "status_code", "n/a"), self._response_snippet(response))
            self._raise_http_error(response, url)

        self._raise_http_error(last_response, url)

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
        from .exceptions import BlueFolderInvalidResponseError

        url = self._build_request_url(action, override_url)
        xml_data = self._coerce_xml_payload(action, xml_data=xml_data, params=params)
        hdrs = self._auth_headers()
        response = self._perform_request(url, xml_data, hdrs, action)

        empty_retry_total = int(os.getenv("BLUEFOLDER_EMPTY_RESPONSE_RETRY_TOTAL") or 2)
        empty_retry_backoff = float(os.getenv("BLUEFOLDER_EMPTY_RESPONSE_RETRY_BACKOFF") or 0.25)
        can_retry_empty = self._is_retryable_action(action)

        for attempt in range(empty_retry_total + 1):
            try:
                return ET.fromstring(response.content)
            except ET.ParseError as e:
                resp_headers = getattr(response, "headers", {}) or {}
                resp_text = getattr(response, "text", "")
                resp_status = getattr(response, "status_code", "n/a")
                is_empty_response = not str(resp_text).strip()
                should_retry = is_empty_response and can_retry_empty and attempt < empty_retry_total

                if should_retry:
                    logger.warning(
                        "Invalid XML from %s (status=%s, headers=%s), retrying empty response (%s/%s).",
                        url,
                        resp_status,
                        dict(resp_headers),
                        attempt + 1,
                        empty_retry_total,
                    )
                    time.sleep(empty_retry_backoff * (attempt + 1))
                    response = self._perform_request(url, xml_data, hdrs, action)
                    continue

                log_message = "Invalid XML from %s (status=%s, headers=%s):\n%s"
                log_args = (url, resp_status, dict(resp_headers), resp_text)
                if is_empty_response:
                    logger.warning(*((log_message,) + log_args))
                else:
                    logger.error(*((log_message,) + log_args))
                raise BlueFolderInvalidResponseError("Invalid XML response") from e

    def _post_response(self, action: str, xml_data=None, params=None, override_url: str = None):
        """Perform a POST and return the raw response object."""
        url = self._build_request_url(action, override_url)
        xml_data = self._coerce_xml_payload(action, xml_data=xml_data, params=params)
        hdrs = self._auth_headers()
        return self._perform_request(url, xml_data, hdrs, action)

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
        headers = self._auth_headers()
        logger.debug(f"POST → {url}\n{xml_body}")

        response = self._perform_request(url, xml_body.encode("utf-8"), headers, endpoint)
        return response.text

    # -------------------------------------------------------------------------
    # Common CRUD-style operations
    # -------------------------------------------------------------------------
    def get(self, params: dict = None):
        """Perform a standard `get` operation."""
        self._warn_or_block_generic_helper("get")
        return self._post("get", params=params)

    def list(self, params: dict = None):
        """Perform a standard `list` operation."""
        self._warn_or_block_generic_helper("list")
        return self._post("list", params=params)

    def create(self, params: dict):
        """Perform a standard `add` (create) operation."""
        self._warn_or_block_generic_helper("create")
        return self._post("add", params=params)

    def update(self, params: dict):
        """Perform a standard `edit` (update) operation."""
        self._warn_or_block_generic_helper("update")
        return self._post("edit", params=params)

    # Uncomment if your API supports deletes:
    # def delete(self, params: dict):
    #     """Perform a standard `delete` operation."""
    #     return self._post("delete", params=params)
