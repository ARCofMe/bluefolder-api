from .base import BlueFolderBase

class Customers(BlueFolderBase):
    def list_customers(self, active_only=True):
        return self._request("POST", "Customers/List", {"ActiveOnly": active_only})

    def get_customer_by_id(self, customer_id):
        return self._request("POST", "Customers/Get", {"Id": customer_id})
