# equipment.py

from .base import BlueFolderClient


class BlueFolderEquipment(BlueFolderClient):
    """
    Handles interaction with the Equipment endpoint of the BlueFolder API.
    """

    def list(self, **params):
        """
        Returns a list of equipment records.
        Optional filters may include customerId, workOrderId, etc.
        """
        return self.get("equipment/list", params=params)

    def get(self, equipment_id: int):
        """
        Retrieves a specific equipment item by ID.
        """
        return super().get("equipment/get", params={"id": equipment_id})
