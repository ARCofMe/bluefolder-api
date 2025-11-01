# tasks.py

from .base import BlueFolderClient


class BlueFolderTasks(BlueFolderClient):
    """
    Handles interaction with the Tasks endpoint of the BlueFolder API.
    """

    def list(self, **params):
        """
        Returns a list of tasks.
        Optional filters may include assignedUserId, workOrderId, etc.
        """
        return self.get("task/list", params=params)

    def get(self, task_id: int):
        """
        Retrieves a specific task by ID.
        """
        return super().get("task/get", params={"id": task_id})
