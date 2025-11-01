from typing import Any
from .base import BlueFolderBase


class BlueFolderCustomers(BlueFolderBase):
    """
    Retrieve BlueFolder customer data.
    """

    def list(self) -> Any:
        return self._request("POST", "Customers/GetList")

    def get(self, customer_id: int) -> Any:
        if not customer_id:
            raise ValueError("Customer ID is required.")
        return self._request("POST", "Customers/Get", {"ID": customer_id})
