# bluefolder_api/customers.py

from base import BlueFolderBase

class BlueFolderCustomers(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Customers")
