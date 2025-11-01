from .base import BlueFolderBase

class Users(BlueFolderBase):
    def list_users(self, active_only=True):
        payload = {"ActiveOnly": active_only}
        return self._request("POST", "Users/List", payload)

    def get_user_by_id(self, user_id):
        payload = {"Id": user_id}
        return self._request("POST", "Users/Get", payload)
