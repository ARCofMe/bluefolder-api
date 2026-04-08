#!/usr/bin/env python3
"""Parse a BlueFolder SR status dropdown HTML snippet and update the local inventory JSON."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bluefolder_api.status_inventory import update_inventory_from_dropdown_html


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY_PATH = ROOT / "bluefolder_status_inventory.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Update BlueFolder status inventory from SR dropdown HTML.")
    parser.add_argument(
        "html_path",
        nargs="?",
        help="Path to a file containing the BlueFolder status dropdown HTML. Reads stdin when omitted.",
    )
    parser.add_argument(
        "--inventory-path",
        default=str(DEFAULT_INVENTORY_PATH),
        help="Path to the JSON inventory file to update.",
    )
    args = parser.parse_args()

    if args.html_path:
        html = Path(args.html_path).read_text()
    else:
        html = sys.stdin.read()
    values = update_inventory_from_dropdown_html(
        html=html,
        inventory_path=args.inventory_path,
    )
    for value in values:
        print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
