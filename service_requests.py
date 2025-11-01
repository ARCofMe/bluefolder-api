from .base import BlueFolderBase

class ServiceRequests(BlueFolderBase):
    def list_service_requests(self, status=None):
        payload = {"Status": status} if status else {}
        return self._request("POST", "ServiceRequests/List", payload)

    def get_service_request_by_id(self, sr_id):
        return self._request("POST", "ServiceRequests/Get", {"Id": sr_id})
