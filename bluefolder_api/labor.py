# bluefolder_api/labor.py

from .base import BlueFolderBase

class BlueFolderLabor(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Labor")
