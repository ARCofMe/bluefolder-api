# tests/test_expenses.py

"""Expenses endpoint tests."""

import xml.etree.ElementTree as ET
from bluefolder_api.expenses import BlueFolderExpenses


def test_expenses_domain():
    d = BlueFolderExpenses()
    assert d.domain == "expenses"


def test_expenses_list(fake_response):
    d = BlueFolderExpenses()
    d.list({"serviceRequestId": "200"})

    xml = ET.fromstring(fake_response.last_data)
    assert xml.find("method").text == "list"
    assert xml.find("serviceRequestId").text == "200"
