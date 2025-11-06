# bluefolder_api/audit_logs.py

from base import BlueFolderBase

class BlueFolderAuditLogs(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="AuditLogs")
