# bluefolder_api/assignments.py

from .base import BlueFolderBase

class BlueFolderAssignments(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Assignments")
