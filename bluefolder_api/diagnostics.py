"""Conservative, shared diagnostics for untrusted upstream XML.

Only recognized diagnostic fields and reviewed message text leave the parser.
Unknown messages are withheld rather than attempting to redact arbitrary data.
"""
import re
import xml.etree.ElementTree as ET

SAFE_MESSAGES = {
    "Invalid date range", "Invalid start date", "Invalid end date",
    "Invalid date field", "Invalid request", "Invalid parameter",
    "Incomplete response", "Authentication failed", "Access denied",
}


def error_details(root):
    details = {}
    # Read only error envelopes, never service-request/customer data.
    for envelope in (root, root.find("./error"), root.find("./result"),
                     root.find("./result/error")):
        if envelope is None:
            continue
        code = envelope.get("code") or envelope.findtext("errorCode") or envelope.findtext("code")
        message = (envelope.findtext("errorMessage") or envelope.findtext("message")
                   or (envelope.text if envelope.tag == "error" else None))
        if code and re.fullmatch(r"[0-9]{1,8}", code.strip()):
            details["code"] = code.strip()
        if message:
            normalized = " ".join(message.split())
            details["message"] = normalized if normalized in SAFE_MESSAGES else "Upstream message withheld"
    return details


def response_error_details(response):
    content = getattr(response, "content", b"")
    if not isinstance(content, (str, bytes)) or len(content) > 65536:
        return {}
    # Reject entity declarations; never process an untrusted DTD.
    upper = content.upper()
    markers = (b"<!DOCTYPE", b"<!ENTITY") if isinstance(content, bytes) else ("<!DOCTYPE", "<!ENTITY")
    if any(marker in upper for marker in markers):
        return {}
    try:
        return error_details(ET.fromstring(content))
    except (ET.ParseError, ValueError):
        return {}
