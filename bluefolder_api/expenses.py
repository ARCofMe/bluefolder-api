"""Expense tracking helpers for BlueFolder service requests."""

import xml.etree.ElementTree as ET
from .base import BlueFolderBase


class BlueFolderExpenses(BlueFolderBase):
    """
    BlueFolder Expenses API interface.

    Handles expense entries (mileage, meals, lodging, misc.) logged
    against Service Requests for reimbursement or billing.
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderExpenses API handler.
        """
        super().__init__("expenses", client=client)

    # -------------------------------------------------------------------------
    def list_for_service_request(self, service_request_id: int):
        """
        Retrieve all expenses for a given Service Request.

        Parameters
        ----------
        service_request_id : int
            Numeric Service Request ID.

        Returns
        -------
        list[dict]
            List of expense entries.
        """
        root = ET.Element("request")
        exp_list = ET.SubElement(root, "expenseList")
        ET.SubElement(exp_list, "serviceRequestId").text = str(service_request_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        xml_response = self._post("list", xml_data=xml_data)
        expenses = []
        for e in xml_response.findall(".//expense"):
            expenses.append(
                {
                    "id": e.findtext("id"),
                    "type": e.findtext("expenseType"),
                    "amount": e.findtext("amount"),
                    "description": e.findtext("description"),
                    "date": e.findtext("dateIncurred"),
                    "userId": e.findtext("userId"),
                    "isBillable": e.findtext("isBillable") == "1",
                }
            )
        return expenses

    # -------------------------------------------------------------------------
    def add_to_service_request(
        self,
        service_request_id: int,
        amount: float,
        expense_type: str,
        description: str = "",
        is_billable: bool = True,
    ):
        """
        Add an expense entry to a Service Request.

        Parameters
        ----------
        service_request_id : int
            Target Service Request ID.
        amount : float
            Expense amount.
        expense_type : str
            Type of expense (e.g., 'Mileage', 'Meal', 'Lodging').
        description : str, optional
            Expense details.
        is_billable : bool, default True
            Whether the expense is billable.

        Returns
        -------
        xml.etree.ElementTree.Element
            Raw XML response from BlueFolder.
        """
        root = ET.Element("request")
        exp_add = ET.SubElement(root, "expenseAdd")
        ET.SubElement(exp_add, "serviceRequestId").text = str(service_request_id)
        ET.SubElement(exp_add, "amount").text = str(amount)
        ET.SubElement(exp_add, "expenseType").text = expense_type
        ET.SubElement(exp_add, "description").text = description
        ET.SubElement(exp_add, "isBillable").text = "1" if is_billable else "0"
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")

        return self._post("add", xml_data=xml_data)
