# bluefolder_api/base.py

import os
import logging
import xml.etree.ElementTree as ET
from abc import ABC
from dotenv import load_dotenv
import requests

load_dotenv()

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

        self.url = f"https://{self.account}.bluefolder.com/api/2.0/xml"

    def _build_xml_request(self, method: str, params: dict = None) -> str:
        root = ET.Element("request")
        ET.SubElement(root, "method").text = method
        ET.SubElement(root, "apikey").text = self.api_key

        if params:
            for key, value in params.items():
                if value is not None:
                    ET.SubElement(root, key).text = str(value)

        return ET.tostring(root, encoding="utf-8", method="xml")

    def _post(self, method: str, params: dict = None) -> ET.Element:
        xml_data = self._build_xml_request(method, params)
        headers = {"Content-Type": "application/xml"}

        logger.debug(
            f"Sending POST to {self.url} with method: {method} and params: {params}"
        )
        response = requests.post(self.url, data=xml_data, headers=headers)

        if response.status_code != 200:
            logger.error(f"Error: {response.status_code} - {response.text}")
            response.raise_for_status()

        try:
            return ET.fromstring(response.content)
        except ET.ParseError as e:
            logger.exception("Failed to parse XML response.")
            raise RuntimeError("Invalid XML response") from e

    def get(self, params: dict = None):
        return self._post("get", params)

    def list(self, params: dict = None):
        return self._post("list", params)

    def create(self, params: dict):
        return self._post("create", params)

    def update(self, params: dict):
        return self._post("update", params)

    def delete(self, params: dict):
        return self._post("delete", params)
