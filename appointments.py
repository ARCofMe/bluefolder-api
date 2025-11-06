# bluefolder_api/appointments.py

from base import BlueFolderBase

class BlueFolderAppointments(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Appointments")
