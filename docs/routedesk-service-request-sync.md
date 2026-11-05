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
