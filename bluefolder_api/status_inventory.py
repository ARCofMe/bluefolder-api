"""Helpers for maintaining local BlueFolder tenant status inventories."""

from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path


STATUS_CATEGORY_KEYWORDS = {
    "parts": ("part", "material", "order", "backorder", "supplier", "vendor"),
    "dispatch": ("schedule", "scheduled", "dispatch", "assign", "route", "reschedule"),
    "field": ("onsite", "on site", "in progress", "diagnos", "return", "callback"),
    "billing": ("invoice", "billing", "billed", "payment", "paid", "collect"),
    "closed": ("closed", "complete", "completed", "cancel", "done"),
}


class _SelectOptionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_option = False
        self._current_value: str | None = None
        self._current_text_parts: list[str] = []
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() != "option":
            return
        self._in_option = True
        attr_map = dict(attrs)
        self._current_value = attr_map.get("value")
        self._current_text_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_option:
            self._current_text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() != "option" or not self._in_option:
            return
        label = "".join(self._current_text_parts).strip()
        value = (self._current_value or label).strip()
        if value:
            self.values.append(value)
        self._in_option = False
        self._current_value = None
        self._current_text_parts = []


def parse_sr_status_dropdown_html(html: str) -> list[str]:
    """Return normalized SR status option values from BlueFolder dropdown HTML."""
    parser = _SelectOptionParser()
    parser.feed(html)
    seen: set[str] = set()
    values: list[str] = []
    for value in parser.values:
        if value in seen:
            continue
        seen.add(value)
        values.append(value)
    return values


def categorize_sr_status(status: str) -> str:
    """Return the Ops Hub workflow category most likely owned by a status."""
    normalized = str(status or "").strip().casefold()
    if not normalized:
        return "unknown"
    for category, keywords in STATUS_CATEGORY_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return category
    if normalized == "open":
        return "dispatch"
    return "other"


def categorize_sr_statuses(statuses: list[str]) -> dict[str, list[str]]:
    """Group tenant SR statuses into coarse Ops Hub workflow categories."""
    grouped: dict[str, list[str]] = {}
    for status in statuses:
        category = categorize_sr_status(status)
        grouped.setdefault(category, []).append(status)
    return grouped


def update_inventory_from_dropdown_html(
    *,
    html: str,
    inventory_path: str | Path,
    source_label: str = "Tenant SR status dropdown",
    source_url: str = "srUpdate.aspx?type=status",
    source_note: str = "Status options captured from the BlueFolder SR update page HTML select element for this tenant.",
) -> list[str]:
    """Parse dropdown HTML and write the normalized SR status list into the inventory file."""
    inventory_file = Path(inventory_path)
    inventory = json.loads(inventory_file.read_text())
    values = parse_sr_status_dropdown_html(html)
    service_request = inventory.setdefault("service_request", {})
    service_request["tenant_ui_status_options"] = values
    service_request["ops_hub_categories"] = categorize_sr_statuses(values)

    sources = inventory.setdefault("sources", {})
    docs = sources.setdefault("docs", [])
    for entry in docs:
        if entry.get("label") == source_label:
            entry["url"] = source_url
            entry["note"] = source_note
            break
    else:
        docs.append(
            {
                "label": source_label,
                "url": source_url,
                "note": source_note,
            }
        )

    inventory_file.write_text(json.dumps(inventory, indent=2, sort_keys=False) + "\n")
    return values
