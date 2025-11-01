from .base import BlueFolderBase

class Tasks(BlueFolderBase):
    def list_tasks(self, status=None):
        payload = {"Status": status} if status else {}
        return self._request("POST", "Tasks/List", payload)

    def get_task_by_id(self, task_id):
        return self._request("POST", "Tasks/Get", {"Id": task_id})
