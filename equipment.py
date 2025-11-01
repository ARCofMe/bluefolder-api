from .base import BlueFolderBase

class Equipment(BlueFolderBase):
    def list_equipment(self, customer_id=None):
        payload = {"CustomerId": customer_id} if customer_id else {}
        return self._request("POST", "Equipment/List", payload)

    def get_equipment_by_id(self, equipment_id):
        return self._request("POST", "Equipment/Get", {"Id": equipment_id})
