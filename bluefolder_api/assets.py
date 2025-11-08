# bluefolder_api/assets.py

from .base import BlueFolderBase

class BlueFolderAssets(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Assets")
