#!/usr/bin/env python3
"""Export live BlueFolder status observations for the configured tenant."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from bluefolder_api.client import BlueFolderClient


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "bluefolder_status_inventory.json"


def _bluefolder_day(value: date) -> str:
    return value.strftime("%Y.%m.%d")


def _window_pairs(*, days_back: int, window_days: int) -> list[tuple[date, date]]:
    end = date.today()
    start = end - timedelta(days=days_back)
    windows: list[tuple[date, date]] = []
    cursor = start
    while cursor <= end:
        window_end = min(cursor + timedelta(days=window_days - 1), end)
        windows.append((cursor, window_end))
        cursor = window_end + timedelta(days=1)
    return windows


def _extract_sr_statuses(client: BlueFolderClient, *, days_back: int, window_days: int) -> dict[str, object]:
    raw_counter: Counter[str] = Counter()
    scanned = 0
    windows = _window_pairs(days_back=days_back, window_days=window_days)
    sample_method = "service_requests.list_for_range"
    for start, end in windows:
        rows = client.service_requests.list_for_range(
            start_date=f"{_bluefolder_day(start)} 12:00 AM",
            end_date=f"{_bluefolder_day(end)} 11:59 PM",
        )
        for row in rows:
            scanned += 1
            status = str(row.get("status") or row.get("serviceRequestStatus") or "").strip()
            if status:
                raw_counter[status] += 1
    return {
        "sample_method": sample_method,
        "scanned_service_requests": scanned,
        "distinct_statuses": [
            {"value": value, "count": count}
            for value, count in sorted(raw_counter.items(), key=lambda item: (-item[1], item[0].casefold()))
        ],
    }


def _extract_sr_statuses_from_assignments(
    client: BlueFolderClient,
    *,
    days_back: int,
    user_limit: int,
) -> dict[str, object]:
    active_users = client.users.list_active()[:user_limit]
    start = date.today() - timedelta(days=days_back)
    end = date.today()
    service_request_ids: set[str] = set()
    raw_counter: Counter[str] = Counter()
    scanned_assignments = 0

    for user in active_users:
        user_id = user.get("id")
        if not user_id:
            continue
        try:
            rows = client.assignments.list_for_user_range(
                user_id=int(user_id),
                start_date=f"{_bluefolder_day(start)} 12:00 AM",
                end_date=f"{_bluefolder_day(end)} 11:59 PM",
                date_range_type="scheduled",
            )
        except Exception:
            continue
        for row in rows:
            scanned_assignments += 1
            sr_id = str(row.get("serviceRequestId") or "").strip()
            if sr_id:
                service_request_ids.add(sr_id)

    for sr_id in sorted(service_request_ids):
        try:
            sr = client.service_requests.get_by_id(int(sr_id))
        except Exception:
            continue
        status = str(
            sr.findtext(".//serviceRequestStatus")
            or sr.findtext(".//serviceRequestStatusName")
            or sr.findtext(".//status")
            or sr.findtext(".//statusName")
            or ""
        ).strip()
        if status:
            raw_counter[status] += 1

    return {
        "sample_method": "assignments -> service_requests.get_by_id fallback",
        "sampled_users": len(active_users),
        "scanned_assignments": scanned_assignments,
        "scanned_service_requests": len(service_request_ids),
        "distinct_statuses": [
            {"value": value, "count": count}
            for value, count in sorted(raw_counter.items(), key=lambda item: (-item[1], item[0].casefold()))
        ],
    }


def _extract_assignment_statuses(
    client: BlueFolderClient,
    *,
    days_back: int,
    user_limit: int,
) -> dict[str, object]:
    active_users = client.users.list_active()[:user_limit]
    raw_counter: Counter[str] = Counter()
    normalized_counter: Counter[str] = Counter()
    scanned = 0
    start = date.today() - timedelta(days=days_back)
    end = date.today()
    for user in active_users:
        user_id = user.get("id")
        if not user_id:
            continue
        try:
            rows = client.assignments.list_for_user_range(
                user_id=int(user_id),
                start_date=f"{_bluefolder_day(start)} 12:00 AM",
                end_date=f"{_bluefolder_day(end)} 11:59 PM",
                date_range_type="scheduled",
            )
        except Exception:
            continue
        for row in rows:
            scanned += 1
            raw_status = str(row.get("status") or "").strip()
            if raw_status:
                raw_counter[raw_status] += 1
            normalized = "complete" if str(row.get("isComplete")).lower() in {"1", "true", "yes"} else "scheduled"
            normalized_counter[normalized] += 1
    return {
        "sampled_users": len(active_users),
        "scanned_assignments": scanned,
        "distinct_raw_statuses": [
            {"value": value, "count": count}
            for value, count in sorted(raw_counter.items(), key=lambda item: (-item[1], item[0].casefold()))
        ],
        "distinct_normalized_statuses": [
            {"value": value, "count": count}
            for value, count in sorted(normalized_counter.items(), key=lambda item: (-item[1], item[0].casefold()))
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export live BlueFolder status inventory.")
    parser.add_argument("--days-back", type=int, default=365)
    parser.add_argument("--window-days", type=int, default=31)
    parser.add_argument("--assignment-days-back", type=int, default=30)
    parser.add_argument("--assignment-user-limit", type=int, default=25)
    args = parser.parse_args()

    client = BlueFolderClient()
    inventory = json.loads(OUTPUT_PATH.read_text())
    service_request_inventory = _extract_sr_statuses(
        client,
        days_back=args.days_back,
        window_days=args.window_days,
    )
    if (
        not service_request_inventory["distinct_statuses"]
        and int(service_request_inventory["scanned_service_requests"]) == 0
    ):
        service_request_inventory = _extract_sr_statuses_from_assignments(
            client,
            days_back=args.assignment_days_back,
            user_limit=args.assignment_user_limit,
        )
    inventory["live_tenant_extract"] = {
        "generated_at": date.today().isoformat(),
        "service_request": service_request_inventory,
        "assignment": _extract_assignment_statuses(
            client,
            days_back=args.assignment_days_back,
            user_limit=args.assignment_user_limit,
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(inventory, indent=2, sort_keys=False) + "\n")
    print(json.dumps(inventory["live_tenant_extract"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
