from typing import Dict, Optional, Any
from .base import BlueFolderBase


class BlueFolderAppointments(BlueFolderBase):
    """
    Handles API calls related to appointments.
    """

    def list(self, start_date: str, end_date: str, user_id: Optional[int] = None) -> Any:
        if not start_date or not end_date:
            raise ValueError("Start and end dates must be provided.")
        payload = {
            "StartDate": start_date,
            "EndDate": end_date
        }
        if user_id:
            payload["UserID"] = user_id
        return self._request("POST", "Appointments/GetList", payload)

    def get(self, appointment_id: int) -> Any:
        if not appointment_id:
            raise ValueError("Appointment ID is required.")
        return self._request("POST", "Appointments/Get", {"ID": appointment_id})
