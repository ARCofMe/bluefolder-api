# bluefolder_api/comments.py

from base import BlueFolderBase

class BlueFolderComments(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Comments")
