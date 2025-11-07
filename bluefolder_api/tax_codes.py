# bluefolder_api/tax_codes.py

from .base import BlueFolderBase

class BlueFolderTaxCodes(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="TaxCodes")
