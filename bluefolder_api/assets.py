"""BlueFolder Assets domain wrapper."""

from .base import BlueFolderBase


class BlueFolderAssets(BlueFolderBase):
    """Expose CRUD helpers for the BlueFolder assets domain."""

    def __init__(self):
        """Initialize the assets domain using the shared client context."""
        super().__init__(domain="Assets")
