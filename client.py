import os
import logging
from dotenv import load_dotenv

from .appointments import BlueFolderAppointments
from .users import BlueFolderUsers
from .customers import BlueFolderCustomers
from .tasks import BlueFolderTasks
from .equipment import BlueFolderEquipment
from .base import BlueFolderBase

# Load from .env if available
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlueFolderClient:
    """
    Central client for accessing all BlueFolder API domains.
    """

    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("BLUEFOLDER_API_KEY")
        self.base_url = base_url or os.getenv("BLUEFOLDER_BASE_URL", "https://app.bluefolder.com/api/2.0/json/")

        if not self.api_key:
            raise EnvironmentError("BLUEFOLDER_API_KEY must be set in environment or passed to the client.")

        logger.info("Initializing BlueFolder client")

        # Shared base object
        self._base = BlueFolderBase(api_key=self.api_key, base_url=self.base_url)

        # Lazy-loaded domain clients
        self._appointments = None
        self._users = None
        self._customers = None
        self._tasks = None
        self._equipment = None

    @property
    def appointments(self) -> BlueFolderAppointments:
        if not self._appointments:
            self._appointments = BlueFolderAppointments(self.api_key, self.base_url)
        return self._appointments

    @property
    def users(self) -> BlueFolderUsers:
        if not self._users:
            self._users = BlueFolderUsers(self.api_key, self.base_url)
        return self._users

    @property
    def customers(self) -> BlueFolderCustomers:
        if not self._customers:
            self._customers = BlueFolderCustomers(self.api_key, self.base_url)
        return self._customers

    @property
    def tasks(self) -> BlueFolderTasks:
        if not self._tasks:
            self._tasks = BlueFolderTasks(self.api_key, self.base_url)
        return self._tasks

    @property
    def equipment(self) -> BlueFolderEquipment:
        if not self._equipment:
            self._equipment = BlueFolderEquipment(self.api_key, self.base_url)
        return self._equipment
