import logging
import os

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
from .base import _build_default_base_url, _infer_account_from_base_url

# -------------------------------------------------------------------------
# Load environment
# -------------------------------------------------------------------------
load_dotenv()
logger = logging.getLogger(__name__)


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
        resolved_base_url = base_url or os.getenv("BLUEFOLDER_BASE_URL")
        self.account = os.getenv("BLUEFOLDER_ACCOUNT_NAME") or _infer_account_from_base_url(resolved_base_url)

        if not self.api_key:
            raise ValueError("Missing BLUEFOLDER_API_KEY")

        self.base_url = (resolved_base_url or _build_default_base_url(self.account)).rstrip("/")

        # Create a single persistent HTTP session (shared across all domains)
        self.session = requests.Session()

        logger.debug("Initialized BlueFolderClient with base_url=%s", self.base_url)

        # Domain clients (each inherits this client for shared context)
        self.appointments = BlueFolderAppointments(client=self)
        self.assignments = BlueFolderAssignments(client=self)
        self.attachments = BlueFolderAttachments(client=self)
        self.comments = BlueFolderComments(client=self)
        self.contracts = BlueFolderContracts(client=self)
        self.custom_fields = BlueFolderCustomFields(client=self)
        self.customers = BlueFolderCustomers(client=self)
        self.customer_contacts = BlueFolderCustomerContacts(client=self)
        self.customer_locations = BlueFolderCustomerLocations(client=self)
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
