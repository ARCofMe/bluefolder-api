# Customer location connector contract

Read-only action: `GET /customer-locations/{locationId}`.
Use a positive numeric **customer location ID** (the `customerLocationId` on an SR),
not its customer ID or the customer's primary location. No customerId parameter
is needed. Existing `X-ARCOM-API-Key` authentication applies when configured.

The SDK sends the documented XML to `/api/2.0/customers/getLocation.aspx`:

```xml
<request><customerLocationGet><customerLocationId>456</customerLocationId></customerLocationGet></request>
```

## Synthetic success response for connector setup

```json
{
  "customerLocation": {
    "id": "456",
    "customerId": "123",
    "name": "Test Unit 2",
    "isPrimary": true,
    "address": "123 Example Street",
    "city": "Rockland",
    "state": "ME",
    "zip": "04841",
    "country": "United States",
    "formattedAddress": "123 Example Street, Rockland ME 04841",
    "notes": "Test only",
    "zone": "  Midcoast / Friday  ",
    "phone": "207-555-0100",
    "primaryContactId": "88",
    "serviceManagerId": "99",
    "technicianId": "100"
  }
}
```

Existing SDK keys are retained. Country, phone and primaryContactId are additive.
IDs are strings or null. Missing text fields are empty strings. isPrimary is boolean.
Zone text is preserved exactly, including whitespace, for later reconciliation.
A zone does not establish territory, service-day availability, technician coverage
or an appointment; review distinct values before normalization and import.

| Status | Meaning |
| --- | --- |
| 200 | Location retrieved |
| 400 | Invalid/nonpositive location ID |
| 401 | Wrapper-key check rejected request |
| 404 | Successful BlueFolder response has no location |
| 502 | Typed SDK failure, XML-level rejection, or missing/different returned location ID |

SDK failures use a generic JSON error without echoing raw upstream payloads.
Malformed XML follows existing base SDK invalid-response handling.

SDK usage: `bf.customer_locations.get_location(456)` returns the normalized dictionary.
This fixes its get URL/payload only; location enumeration, mutations and the separate
legacy `customers.get_location_by_id` raw XML helper are unchanged.

Tests use fake sessions. Merge/deploy, verify one known location against BlueFolder,
then create the connector action. Deployment, connector setup and batch import are
not performed by this change. No BlueFolder or Dataverse writes are introduced.
