from bluefolder_api.status_inventory import (
    categorize_sr_status,
    categorize_sr_statuses,
    load_status_inventory,
    parse_sr_status_dropdown_html,
    tenant_service_request_statuses,
    update_inventory_from_dropdown_html,
)


def test_parse_sr_status_dropdown_html_deduplicates_and_preserves_order():
    html = """
    <select name="ctl00$MainContent$NewStatus$StatusList" id="StatusList" class="form-control">
        <option value="New">New</option>
        <option value="Completed" selected="selected">Completed</option>
        <option value="New">New</option>
        <option>Waiting on CX</option>
    </select>
    """

    assert parse_sr_status_dropdown_html(html) == [
        "New",
        "Completed",
        "Waiting on CX",
    ]


def test_update_inventory_from_dropdown_html_updates_json(tmp_path):
    inventory_path = tmp_path / "inventory.json"
    inventory_path.write_text('{"sources":{"docs":[]},"service_request":{}}')

    values = update_inventory_from_dropdown_html(
        html="""
        <select>
            <option value="New">New</option>
            <option value="Scheduled">Scheduled</option>
        </select>
        """,
        inventory_path=inventory_path,
    )

    assert values == ["New", "Scheduled"]
    assert '"tenant_ui_status_options": [\n      "New",\n      "Scheduled"\n    ]' in inventory_path.read_text()
    assert '"dispatch": [\n        "Scheduled"\n      ]' in inventory_path.read_text()


def test_categorize_sr_statuses_groups_ops_hub_workflows():
    assert categorize_sr_status("Need Parts/Schedule") == "parts"
    assert categorize_sr_status("Scheduled") == "dispatch"
    assert categorize_sr_status("Completed") == "closed"
    assert categorize_sr_status("") == "unknown"
    assert categorize_sr_statuses(["Need Parts/Schedule", "Need Parts/Schedule", "Waiting on Billing"]) == {
        "parts": ["Need Parts/Schedule"],
        "billing": ["Waiting on Billing"],
    }


def test_tenant_service_request_statuses_reads_observed_and_live_inventory():
    inventory = {
        "service_request": {
            "observed_status_values": [{"value": "New"}, {"value": "Completed"}],
        },
        "live_tenant_extract": {
            "service_request": {
                "distinct_statuses": [
                    {"value": "Need Parts/Schedule", "count": 4},
                    {"value": "completed", "count": 1},
                ]
            }
        },
    }

    assert tenant_service_request_statuses(inventory) == ["New", "Completed", "Need Parts/Schedule"]


def test_load_status_inventory_rejects_missing_or_invalid_files(tmp_path):
    missing_path = tmp_path / "missing.json"
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("[]")

    try:
        load_status_inventory(missing_path)
    except ValueError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("missing inventory should fail")

    try:
        load_status_inventory(invalid_path)
    except ValueError as exc:
        assert "JSON object" in str(exc)
    else:
        raise AssertionError("non-object inventory should fail")
