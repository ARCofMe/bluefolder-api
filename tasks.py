from typing import Any
from .base import BlueFolderBase


class BlueFolderTasks(BlueFolderBase):
    """
    Retrieve BlueFolder tasks.
    """

    def list(self) -> Any:
        return self._request("POST", "Tasks/GetList")

    def get(self, task_id: int) -> Any:
        if not task_id:
            raise ValueError("Task ID is required.")
        return self._request("POST", "Tasks/Get", {"ID": task_id})
