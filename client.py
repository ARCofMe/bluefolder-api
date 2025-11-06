# bluefolder_api/client.py

from .appointments import BlueFolderAppointments
from .assignments import BlueFolderAssignments
from .attachments import BlueFolderAttachments
from .comments import BlueFolderComments
from .contracts import BlueFolderContracts
from .custom_fields import BlueFolderCustomFields
from .customer_contacts import BlueFolderCustomerContacts
from .customer_locations import BlueFolderCustomerLocations
from .customers import BlueFolderCustomers
from .equipment import BlueFolderEquipment
from .expenses import BlueFolderExpenses
from .item_lists import BlueFolderItemLists
from .labor import BlueFolderLabor
from .materials import BlueFolderMaterials
from .service_requests import BlueFolderServiceRequests
from .tax_codes import BlueFolderTaxCodes
from .users import BlueFolderUsers


class BlueFolderClient:
    def __init__(self):
        self.appointments = BlueFolderAppointments()
        self.assignments = BlueFolderAssignments()
        self.attachments = BlueFolderAttachments()
        self.comments = BlueFolderComments()
        self.contracts = BlueFolderContracts()
        self.custom_fields = BlueFolderCustomFields()
        self.customer_contacts = BlueFolderCustomerContacts()
        self.customer_locations = BlueFolderCustomerLocations()
        self.customers = BlueFolderCustomers()
        self.equipment = BlueFolderEquipment()
        self.expenses = BlueFolderExpenses()
        self.item_lists = BlueFolderItemLists()
        self.labor = BlueFolderLabor()
        self.materials = BlueFolderMaterials()
        self.service_requests = BlueFolderServiceRequests()
        self.tax_codes = BlueFolderTaxCodes()
        self.users = BlueFolderUsers()

    def __repr__(self):
        return "<BlueFolderClient: available domains = [appointments, assignments, attachments, comments, contracts, custom_fields, customer_contacts, customer_locations, customers, equipment, expenses, item_lists, labor, materials, service_requests, tax_codes, users]>"
