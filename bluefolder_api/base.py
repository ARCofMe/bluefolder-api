# bluefolder_api/base.py

import os
import logging
import xml.etree.ElementTree as ET
from abc import ABC
from dotenv import load_dotenv
import requests

# Locate .env file relative to this file or the current working directory
env_path = os.getenv("BLUEFOLDER_ENV_PATH")  # optional override
if not env_path:
    # Try same directory as base.py or its parent
    here = os.path.dirname(os.path.abspath(__file__))
    # walk up one directory to project root
    candidate = os.path.join(os.path.dirname(here), ".env")
    if os.path.exists(candidate):
        env_path = candidate
    else:
        # fallback: current working directory
        env_path = os.path.join(os.getcwd(), ".env")

load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BlueFolderBase(ABC):
    def __init__(self, domain: str):
        self.api_key = os.getenv("BLUEFOLDER_API_KEY")
        self.account = os.getenv("BLUEFOLDER_ACCOUNT_NAME")
        self.domain = domain

        if not self.api_key or not self.account:
            raise ValueError(
                "Missing BLUEFOLDER_API_KEY or BLUEFOLDER_ACCOUNT_NAME in .env"
            )

        # Base per-domain URL
        self.base_url = f"https://{self.account}.bluefolder.com/api/2.0/"

    def _build_xml_request(self, params: dict | None = None) -> bytes:
        """
        Build the <request> body the way the docs show:

        <request>
          <apikey>...</apikey>
          <someParam>...</someParam>
        </request>
        """
        root = ET.Element("request")
        ET.SubElement(root, "apikey").text = self.api_key

        if params:
            for key, value in params.items():
                if value is not None:
                    ET.SubElement(root, key).text = str(value)

        return ET.tostring(root, encoding="utf-8", method="xml")

    def _post(self, action: str, xml_data=None, params=None, override_url: str = None):
        import xml.etree.ElementTree as ET
        import base64
        import logging
        import requests

        logger = logging.getLogger(__name__)

        # ensure we don't get double slashes
        url = override_url or f"{self.base_url.rstrip('/')}/{self.domain}/{action}.aspx"

        if xml_data is None:
            xml_data = self._build_xml_request(action, params)

        # BlueFolder expects api_key first, then account name
        credentials = f"{self.api_key}:{self.account}"
        token = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Content-Type": "application/xml",
            "Authorization": f"Basic {token}",
        }

        logger.debug(f"POST → {url}\n{xml_data.decode()}")
        response = requests.post(url, data=xml_data, headers=headers)

        logger.debug(f"Status: {response.status_code}")
        logger.debug(f"Response:\n{response.text}")

        if response.status_code != 200:
            logger.error(f"Error {response.status_code}: {response.text}")
            response.raise_for_status()

        try:
            return ET.fromstring(response.content)
        except ET.ParseError as e:
            logger.error(f"Invalid XML from {url}:\n{response.text}")
            raise RuntimeError("Invalid XML response") from e





    def get(self, params: dict = None):
        return self._post("get", params)

    def list(self, params: dict = None):
        return self._post("list", params)

    def create(self, params: dict):
        return self._post("add", params)

    def update(self, params: dict):
        return self._post("edit", params)

    #def delete(self, params: dict):
    #    return self._post("delete", params)
