# bluefolder_api/service_requests.py

from base import BlueFolderBase

class BlueFolderServiceRequests(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="ServiceRequests")
