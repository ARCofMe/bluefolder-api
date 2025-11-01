from .base import BlueFolderBase

class Appointments(BlueFolderBase):
    def list_appointments(self, start_date=None, end_date=None):
        payload = {}
        if start_date:
            payload["StartDate"] = start_date
        if end_date:
            payload["EndDate"] = end_date
        return self._request("POST", "Appointments/List", payload)

    def get_appointment_by_id(self, appointment_id):
        return self._request("POST", "Appointments/Get", {"Id": appointment_id})
