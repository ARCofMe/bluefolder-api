from .base import BlueFolderBase

class Materials(BlueFolderBase):
    def list_materials(self, customer_id=None):
        payload = {"CustomerId": customer_id} if customer_id else {}
        return self._request("POST", "Materials/List", payload)

    def get_material_by_id(self, material_id):
        return self._request("POST", "Materials/Get", {"Id": material_id})
