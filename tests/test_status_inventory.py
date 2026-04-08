from bluefolder_api.status_inventory import (
    parse_sr_status_dropdown_html,
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
