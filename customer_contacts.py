# bluefolder_api/customer_contacts.py

from .base import BlueFolderBase

class BlueFolderCustomerContacts(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="CustomerContacts")
