"""Domain wrapper for querying BlueFolder audit logs."""

from .base import BlueFolderBase


class BlueFolderAuditLogs(BlueFolderBase):
    """Expose helper methods for the audit logs API endpoints."""

    def __init__(self):
        """Initialize the audit logs domain with the shared client session."""
        super().__init__(domain="AuditLogs")
