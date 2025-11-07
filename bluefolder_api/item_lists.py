# bluefolder_api/item_lists.py

from base import BlueFolderBase

class BlueFolderItemLists(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="ItemLists")
