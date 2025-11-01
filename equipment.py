from typing import Dict, Any
from .base import BlueFolderBase


class BlueFolderEquipment(BlueFolderBase):
    """
    Manages BlueFolder Equipment endpoints.
    """

    def get(self, equipment_id: int) -> Any:
        if not equipment_id:
            raise ValueError("Equipment ID is required.")
        return self._request("POST", "Equipment/Get", {"ID": equipment_id})

    def list(self, customer_id: int) -> Any:
        if not customer_id:
            raise ValueError("Customer ID is required.")
        return self._request("POST", "Equipment/GetList", {"CustomerID": customer_id})
