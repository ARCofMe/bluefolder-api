# bluefolder_api/custom_fields.py

from .base import BlueFolderBase

class BlueFolderCustomFields(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="CustomFields")
