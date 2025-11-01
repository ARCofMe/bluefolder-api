# bluefolder_api/appointments.py
from .base import BlueFolderClient

class BlueFolderAppointments(BlueFolderClient):
    """Handles API operations related to Appointments."""

    def list(self, user_id=None, date_start=None, date_end=None):
        return self.request("appointment.list", {
            "userId": user_id,
            "dateRangeStart": date_start,
            "dateRangeEnd": date_end
        })

    def get(self, appointment_id):
        return self.request("appointment.get", {
            "appointmentId": appointment_id
        })