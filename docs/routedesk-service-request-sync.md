# RouteDesk Service Request Sync

The JSON facade already supports these optional query parameters on `GET /service-requests`:

- `startDate`, `endDate`: required ISO dates (`YYYY-MM-DD`), inclusive, at most 31 calendar days.
- `dateField`: `dateTimeCreated` (default) or `dateTimeClosed`.
- `status`: optional BlueFolder status filter; `open` requests non-closed service requests **within the specified date window**.

Examples:

```http
GET /service-requests?startDate=2026-11-01&endDate=2026-11-05
GET /service-requests?startDate=2026-11-01&endDate=2026-11-05&status=open
GET /service-requests?startDate=2026-11-01&endDate=2026-11-05&dateField=dateTimeClosed
```

## Suggested synchronization passes

1. **Created:** Poll recent `dateTimeCreated` windows to discover new records.
2. **Open:** Scan *multiple bounded creation-date windows* with `status=open` to refresh active records. A single recent window will miss older open tickets.
3. **Closed:** Poll recent `dateTimeClosed` windows to catch closures.
4. **Reconciliation:** Periodically revisit older windows and/or fetch known service-request IDs individually to catch edits that cannot be identified from creation/closure dates.

BlueFolder's documented list date fields do **not** include a general last-modified timestamp. These passes are a pragmatic reconciliation strategy, **not** a guaranteed real-time change feed. Do not claim complete coverage without a full inventory/reconciliation plan.

## Power Automate and Dataverse safeguards

- Match by the BlueFolder Service Request ID; update if found, create if missing.
- Preserve RouteDesk-owned `Dispatch Stage` when updating an existing record.
- Do not erase manually enriched values when BlueFolder returns null without an explicit field-ownership policy.
- Do not interpret absence from an `open` result as proof of closure or delete records.
- Keep original source text where possible; the existing 4,000-character Complaint mapping can truncate long manufacturer emails.
- Test a small date window and inspect Dataverse writes before scheduling recurring runs.
- Avoid parallel overlapping sync passes until duplicate prevention and conflict behavior are verified.

## Future enhancement

Consider a dedicated reconciliation workflow with a persisted window cursor, known-ticket refresh, run metrics, and retry handling. Do not increase the facade's 31-day limit merely because upstream documentation permits larger windows; review operational cost and pagination/response size first.


## List-query error diagnostics

XML `response status="fail"` and trailing `result status="fail"` previously
became generic ValueErrors, discarding upstream error fields. They now retain
sanitized `upstreamError` fields in JSON (HTTP 400, as before). HTTP transport
failures remain HTTP 502 in the facade and include `httpStatus` when available.
Local date validation remains HTTP 400. Success schemas, date conversion, filters,
and retry rules are unchanged.

Structured warning records carry a `bluefolder_error` dictionary. The shared
transport no longer logs raw request/response bodies, response headers, or URLs
in failure messages. Only short numeric error codes and an explicit set of
reviewed generic messages in `bluefolder_api/diagnostics.py` are retained from
error envelopes. Unknown text becomes `Upstream message withheld`; unsupported
codes are omitted. Malformed, non-XML, DTD-bearing, or oversized HTTP error bodies
produce no XML details. This intentionally sacrifices unknown free-text detail
to avoid leaking credentials or customer data. Do not enable raw payload logging
to fill that gap; add reviewed generic messages/shapes with regression tests.

The reported November 1–5 and November 5 successes, and November 6/ranges starting
November 6 failures, do not establish a date-format or timezone defect. No actual
upstream error for that incident has been examined. After deployment through the
normal review process, compare the sanitized code/message for the failing window
with a successful window. An unfamiliar envelope or withheld message may require
secure investigation with BlueFolder support before expanding the allowlist.
