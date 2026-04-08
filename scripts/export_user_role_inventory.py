#!/usr/bin/env python3
"""Export BlueFolder tenant roles plus per-user assigned roles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bluefolder_api.client import BlueFolderClient


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "bluefolder_user_roles.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BlueFolder user role inventory for the configured tenant.")
    parser.add_argument(
        "--output-path",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Path to write the JSON export.",
    )
    parser.add_argument(
        "--active-only",
        action="store_true",
        help="Only include active users in the export.",
    )
    args = parser.parse_args()

    client = BlueFolderClient()
    inventory = client.users.get_role_inventory(include_inactive=not args.active_only)
    output_path = Path(args.output_path)
    output_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
