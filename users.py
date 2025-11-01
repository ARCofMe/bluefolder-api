from typing import Any
from .base import BlueFolderBase


class BlueFolderUsers(BlueFolderBase):
    """
    Access user information from BlueFolder.
    """

    def list(self) -> Any:
        return self._request("POST", "Users/GetList")

    def get(self, user_id: int) -> Any:
        if not user_id:
            raise ValueError("User ID is required.")
        return self._request("POST", "Users/Get", {"ID": user_id})
