"""Customer domain helpers used to resolve locations and metadata."""

import logging
import xml.etree.ElementTree as ET
from .base import BlueFolderBase

logger = logging.getLogger(__name__)


class BlueFolderCustomers(BlueFolderBase):
    """
    BlueFolderCustomers — Handles /customers endpoints.

    Key endpoints supported:
    - /customers/getLocation.aspx
    - /customers/get.aspx (if you ever need full customer detail)
    """

    def __init__(self, client=None):
        """Initialize the customers domain with shared client context."""
        super().__init__(domain="customers", client=client)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def list(self, **filters):
        """List customers with optional filters."""
        root = ET.Element("request")
        cust_list = ET.SubElement(root, "customerList")
        for key, val in filters.items():
            if val is None:
                continue
            ET.SubElement(cust_list, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("list", xml_data=xml_data)

    def add(self, **fields):
        """Create a customer record."""
        root = ET.Element("request")
        cust_add = ET.SubElement(root, "customerAdd")
        for key, val in fields.items():
            if val is None:
                continue
            ET.SubElement(cust_add, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("add", xml_data=xml_data)

    def edit(self, customer_id: int | None = None, external_id: str | None = None, **fields):
        """Edit a customer by ID or externalId."""
        if not customer_id and not external_id:
            raise ValueError("customer_id or external_id is required")
        root = ET.Element("request")
        cust_edit = ET.SubElement(root, "customerEdit")
        if customer_id:
            ET.SubElement(cust_edit, "customerId").text = str(customer_id)
        if external_id:
            ET.SubElement(cust_edit, "externalId").text = external_id
        for key, val in fields.items():
            if val is None:
                continue
            ET.SubElement(cust_edit, key).text = str(val)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("edit", xml_data=xml_data)

    def delete(self, customer_id: int):
        """Delete a customer by ID."""
        root = ET.Element("request")
        cust_del = ET.SubElement(root, "customerDelete")
        ET.SubElement(cust_del, "customerId").text = str(customer_id)
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return self._post("delete", xml_data=xml_data)

    # ------------------------------------------------------------------
    # 📍 Location Lookup (Correct Method)
    # ------------------------------------------------------------------
    def get_location_by_id(self, customer_id: int, location_id: int):
        """
        Retrieve a specific customer location by ID for a known customer.

        This directly maps to BlueFolder's `/customers/getLocation.aspx` endpoint.

        Args:
            customer_id (int): The parent customer ID.
            location_id (int): The specific location ID.

        Returns:
            ElementTree.Element: Parsed XML <response> element
                or an empty <response> if not found / invalid.

        API Reference:
        https://app.bluefolder.com/api/2.0/customers/getLocation.aspx
        """
        if not customer_id or not location_id:
            raise ValueError("Both customer_id and location_id are required")

        logger.info(
            f"Fetching customer location {location_id} for customer {customer_id}"
        )

        xml_data = f"""
        <request>
            <customerLocationGet>
                <customerLocationId>{location_id}</customerLocationId>
                <customerId>{customer_id}</customerId>
            </customerLocationGet>
        </request>
        """

        try:
            xml = self._post("getLocation", xml_data=xml_data.encode("utf-8"))
        except Exception as e:
            logger.error(
                f"Error fetching location {location_id} for customer {customer_id}: {e}"
            )
            return ET.Element("response")

        if xml.find(".//customerLocation") is None:
            logger.warning(
                f"No location found for customerId={customer_id}, locationId={location_id}"
            )
        return xml

    # ------------------------------------------------------------------
    # 🧩 Optional: Retrieve Full Customer Info
    # ------------------------------------------------------------------
    def get_by_id(self, customer_id: int):
        """
        Retrieve full customer record (including all locations, contacts, etc.)
        via /customers/get.aspx
        """
        if not customer_id:
            raise ValueError("customer_id is required")

        xml_data = f"""
        <request>
            <customerId>{customer_id}</customerId>
        </request>
        """
        return self._post("get", xml_data=xml_data)
