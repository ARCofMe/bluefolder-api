"""Domain helpers for working with BlueFolder user records."""

import logging
import xml.etree.ElementTree as ET
from .base import BlueFolderBase

logger = logging.getLogger(__name__)


class BlueFolderUsers(BlueFolderBase):
    """
    BlueFolder Users API interface.

    Provides methods for listing, filtering, and retrieving user details
    from your BlueFolder account. This domain is often used to:
      • Build technician or office staff directories
      • Retrieve user IDs for assignment creation
      • Sync BlueFolder users with internal systems

    Example
    -------
        >>> from bluefolder_api.client import BlueFolderClient
        >>> bf = BlueFolderClient()
        >>> users = bf.users.list_all()
        >>> print(users[:3])  # show first three users
    """

    def __init__(self, client=None):
        """
        Initialize the BlueFolderUsers API handler.

        Parameters
        ----------
        client : BlueFolderClient, optional
            Shared client instance containing base_url, API key, and session.
        """
        super().__init__("users", client=client)

    # -------------------------------------------------------------------------
    # USER LISTING
    # -------------------------------------------------------------------------
    def list_all(self):
        """
        Retrieve all users from the BlueFolder system.

        Posts to:
            /api/2.0/users/list.aspx

        Returns
        -------
        list[dict]
            A list of user dictionaries containing:
                - id (str)
                - firstName (str)
                - lastName (str)
                - email (str)
                - isActive (bool)
                - userType (str)
        """
        xml_response = self._post("list")

        users = []
        for u in xml_response.findall(".//user"):
            users.append(
                {
                    "id": u.findtext("userId"),
                    "firstName": u.findtext("firstName"),
                    "lastName": u.findtext("lastName"),
                    "email": u.findtext("email"),
                    "inactive": u.findtext("inactive") == "1",
                    "userType": u.findtext("userType"),
                }
            )
        return users

    # -------------------------------------------------------------------------
    def list_active(self):
        """
        Retrieve only active users from BlueFolder.

        Returns
        -------
        list[dict]
            List of user dictionaries with inactive == False.
        """
        all_users = self.list_all()
        return [u for u in all_users if not u.get("inactive")]

    # -------------------------------------------------------------------------
    def get_by_id(self, user_id: int):
        """
        Retrieve a specific user by ID.

        Posts to:
            /api/2.0/users/get.aspx

        Parameters
        ----------
        user_id : int
            The numeric user ID to retrieve.

        Returns
        -------
        dict
            Dictionary of user details, or an empty dict if the user is not found.
        """
        root = ET.Element("request")
        user_get = ET.SubElement(root, "userGet")
        ET.SubElement(user_get, "id").text = str(user_id)

        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        xml_response = self._post("get", xml_data=xml_data)

        user_node = xml_response.find(".//user")
        if user_node is None:
            return {}

        return {
            "id": user_node.findtext("id"),
            "firstName": user_node.findtext("firstName"),
            "lastName": user_node.findtext("lastName"),
            "email": user_node.findtext("email"),
            "isActive": user_node.findtext("isActive") == "1",
            "userType": user_node.findtext("userType"),
        }

    # -------------------------------------------------------------------------
    def get_user_roles(self):
        """
        Retrieve the list of available user roles (if supported by API version).

        Posts to:
            /api/2.0/users/listRoles.aspx

        Returns
        -------
        list[str]
            A list of role names (e.g. ["Technician", "Dispatcher", "Administrator"]),
            or an empty list if unsupported or empty.
        """
        try:
            xml_response = self._post("listRoles")
        except Exception as e:
            # Not all tenants or API versions support this endpoint
            import logging

            logging.warning(f"User roles endpoint not supported: {e}")
            return []

        roles = [r.text for r in xml_response.findall(".//role")]
        return roles
