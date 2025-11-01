# bluefolder_api/client.py
from .appointments import BlueFolderAppointments
from .customers import BlueFolderCustomers

class BlueFolderAPI:
    """Convenience wrapper to expose grouped BlueFolder domain clients."""

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.appointments = BlueFolderAppointments(api_key)
        self.customers = BlueFolderCustomers(api_key)