# bluefolder_api/customers.py
from .base import BlueFolderClient

class BlueFolderCustomers(BlueFolderClient):
    """Handles API operations related to Customers."""

    def get(self, customer_id):
        return self.request("customer.get", {
            "customerId": customer_id
        })