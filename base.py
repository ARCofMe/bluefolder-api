# bluefolder_api/base.py

import os
import xml.etree.ElementTree as ET
import requests
from dotenv import load_dotenv
from typing import Dict, Optional

# Load environment variables from .env file
load_dotenv()

class BlueFolderBase:
    def __init__(self, domain: str):
        self.api_key = os.getenv("BLUEFOLDER_API_KEY")
        self.account_name = os.getenv("BLUEFOLDER_ACCOUNT_NAME")
        if not self.api_key or not self.account_name:
            raise ValueError("Missing BLUEFOLDER_API_KEY or BLUEFOLDER_ACCOUNT_NAME in environment.")
        
        self.domain = domain
        self.endpoint = f"https://{self.account_name}.bluefolder.com/api/2.0/xml"
        self.headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": f"https://www.bluefolder.com/api/2.0/{domain}"
        }

    def _build_request_body(self, action: str, params: Dict) -> str:
        root = ET.Element("request")
        action_element = ET.SubElement(root, action)
        for key, value in params.items():
            child = ET.SubElement(action_element, key)
            child.text = str(value)
        return ET.tostring(root, encoding="utf-8", method="xml").decode()

    def _parse_response(self, response: requests.Response) -> Dict:
        if not response.ok:
            raise Exception(f"HTTP Error {response.status_code}: {response.text}")
        root = ET.fromstring(response.text)
        return {child.tag: child.text for child in root.iter() if child is not root}

    def call_api(self, action: str, params: Optional[Dict] = None) -> Dict:
        body = self._build_request_body(action, params or {})
        response = requests.post(self.endpoint, headers=self.headers, data=body)
        return self._parse_response(response)

    def get(self, params: Dict) -> Dict:
        return self.call_api("Get", params)

    def get_list(self, params: Optional[Dict] = None) -> Dict:
        return self.call_api("GetList", params or {})

    def create(self, params: Dict) -> Dict:
        return self.call_api("Create", params)

    def update(self, params: Dict) -> Dict:
        return self.call_api("Update", params)

    def delete(self, params: Dict) -> Dict:
        return self.call_api("Delete", params)
