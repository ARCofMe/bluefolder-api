# bluefolder_api/equipment.py

from base import BlueFolderBase

class BlueFolderEquipment(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Equipment")
