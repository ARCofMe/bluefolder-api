# bluefolder_api/attachments.py

from .base import BlueFolderBase

class BlueFolderAttachments(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Attachments")
