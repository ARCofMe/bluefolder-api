# users.py

from .base import BlueFolderClient


class BlueFolderUsers(BlueFolderClient):
    """
    Handles interaction with the Users endpoint of the BlueFolder API.
    """

    def list(self, **params):
        """
        Returns a list of users.
        Optional params may include filters like isActive, userType, etc.
        """
        return self.get("user/list", params=params)

    def get(self, user_id: int):
        """
        Retrieves a specific user by ID.
        """
        return super().get("user/get", params={"id": user_id})
