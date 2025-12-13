"""Primary entrypoint that wires together every BlueFolder domain client."""

import os
import logging

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - test stub

    def load_dotenv(*args, **kwargs):
        return None


try:
    import requests
except ImportError:  # pragma: no cover - test stub
    from bluefolder_api.base import requests  # type: ignore

# Domain imports
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
from .items import BlueFolderItems
from .labor import BlueFolderLabor
from .materials import BlueFolderMaterials
from .service_requests import BlueFolderServiceRequests
from .tax_codes import BlueFolderTaxCodes
from .users import BlueFolderUsers

# -------------------------------------------------------------------------
# Load environment
# -------------------------------------------------------------------------
load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BlueFolderClient:
    """
    Central API client for interacting with all BlueFolder API domains.

    This class manages:
    - a shared requests.Session for persistent connections
    - base API URL construction from environment
    - authentication credentials (API key and account name)
    - initialization of all domain-specific API handlers

    Environment Variables Required
    ------------------------------
    BLUEFOLDER_API_KEY : str
        Your BlueFolder API key.
    BLUEFOLDER_ACCOUNT_NAME : str
        Your BlueFolder account subdomain (e.g., "mycompany" for mycompany.bluefolder.com).

    Example
    -------
        >>> from bluefolder_api.client import BlueFolderClient
        >>> bf = BlueFolderClient()
        >>> users = bf.users.list()
        >>> print(users)
    """
    
    def __init__(self, base_url: str | None = None):
        """Instantiate the shared HTTP session and all domain-specific clients."""
        # Load core credentials
        self.api_key = os.getenv("BLUEFOLDER_API_KEY")
        self.account = os.getenv("BLUEFOLDER_ACCOUNT_NAME")

        if not self.api_key or (not self.account and not base_url):
            raise ValueError("Missing BLUEFOLDER_API_KEY or BLUEFOLDER_ACCOUNT_NAME/base_url")

        if base_url:
            self.base_url = base_url.rstrip("/")
        else:
            # Build the base API URL once, centrally
            self.base_url = f"https://{self.account}.bluefolder.com/api/2.0"

        # Create a single persistent HTTP session (shared across all domains)
        self.session = requests.Session()

        logger.debug(f"Initialized BlueFolderClient with base_url={self.base_url}")

        # Domain clients (each inherits this client for shared context)
        self.appointments = BlueFolderAppointments(client=self)
        self.assignments = BlueFolderAssignments(client=self)
        self.attachments = BlueFolderAttachments(client=self)
        self.comments = BlueFolderComments(client=self)
        self.contracts = BlueFolderContracts(client=self)
        self.custom_fields = BlueFolderCustomFields(client=self)
        self.customer_contacts = BlueFolderCustomerContacts(client=self)
        self.customer_locations = BlueFolderCustomerLocations(client=self)
        self.customers = BlueFolderCustomers(client=self)
        self.equipment = BlueFolderEquipment(client=self)
        self.expenses = BlueFolderExpenses(client=self)
        self.item_lists = BlueFolderItemLists(client=self)
        self.items = BlueFolderItems(client=self)
        self.labor = BlueFolderLabor(client=self)
        self.materials = BlueFolderMaterials(client=self)
        self.service_requests = BlueFolderServiceRequests(client=self)
        self.tax_codes = BlueFolderTaxCodes(client=self)
        self.users = BlueFolderUsers(client=self)

    def __repr__(self):
        """Readable client summary with all available domain interfaces."""
        return (
            "<BlueFolderClient domains=["
            "appointments, assignments, attachments, comments, contracts, "
            "custom_fields, customer_contacts, customer_locations, customers, "
            "equipment, expenses, item_lists, labor, materials, "
            "items, service_requests, tax_codes, users]>"
        )
