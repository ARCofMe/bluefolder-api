# bluefolder_api/users.py

from .base import BlueFolderBase

class BlueFolderUsers(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Users")
