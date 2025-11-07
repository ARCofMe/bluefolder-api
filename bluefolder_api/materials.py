# bluefolder_api/materials.py

from .base import BlueFolderBase

class BlueFolderMaterials(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Materials")
