"""Small JSON/HTTP facade for Power Platform and other integrations."""

import os
import xml.etree.ElementTree as ET
from datetime import date

from flask import Flask, jsonify, request

from .client import BlueFolderClient
from .exceptions import BlueFolderError


def create_app(client_factory=BlueFolderClient):
    """Create the ARCoM BlueFolder JSON facade."""
    app = Flask(__name__)

    def _authorized() -> bool:
        expected = os.getenv("ARCOM_WRAPPER_API_KEY")
        if not expected:
            return True
        return request.headers.get("X-ARCOM-API-Key") == expected

    @app.before_request
    def require_wrapper_key():
        if request.path == "/health":
            return None
        if not _authorized():
            return jsonify({"error": "unauthorized"}), 401
        return None

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/users")
    def users():
        try:
            active_only = request.args.get("activeOnly", "false").lower() in {"1", "true", "yes"}
            client = client_factory()
            rows = client.users.list_active() if active_only else client.users.list_all()
            return jsonify({"users": rows})
        except (BlueFolderError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 502

    @app.get("/service-requests/<int:service_request_id>")
    def service_request(service_request_id):
        try:
            client = client_factory()
            xml_response = client.service_requests.get_by_id(service_request_id)
            sr = xml_response.find(".//serviceRequest")
            if sr is None and xml_response.tag == "serviceRequest":
                sr = xml_response
            if sr is None:
                return jsonify({"error": "service request not found"}), 404
            return jsonify({"serviceRequest": client.service_requests._parse_service_request(sr)})
        except (BlueFolderError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 502

    @app.get("/items/<int:item_id>")
    def item(item_id):
        try:
            client = client_factory()
            xml_response = client.items.get(item_id)

            item_node = xml_response.find(".//item")
            if item_node is None and xml_response.tag == "item":
                item_node = xml_response
            if item_node is None:
                return jsonify({"error": "item not found"}), 404

            def first_text(*names):
                for name in names:
                    value = item_node.findtext(name)
                    if value is not None:
                        return value
                return None

            return jsonify({
                "item": {
                    "id": first_text("itemId", "id"),
                    "itemNo": first_text("itemNo"),
                    "description": first_text("description", "itemDescription"),
                    "manufacturerItemNo": first_text("manufacturerItemNo", "mfrItemNo"),
                    "manufacturerDescription": first_text("manufacturerDescription", "mfrDescription"),
                    "manufacturerName": first_text("manufacturerName", "mfrName"),
                    "cost": first_text("cost", "unitCost"),
                    "price": first_text("price", "unitPrice"),
                }
            })
        except (BlueFolderError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 502

    @app.get("/service-requests/<int:service_request_id>/materials")
    def service_request_materials(service_request_id):
        try:
            client = client_factory()
            xml_response = client.service_requests.get_by_id(service_request_id)
            sr = xml_response.find(".//serviceRequest")
            if sr is None and xml_response.tag == "serviceRequest":
                sr = xml_response
            if sr is None:
                return jsonify({"error": "service request not found"}), 404

            rows = []
            material_nodes = sr.findall("./materials/materialsItem")
            if not material_nodes:
                material_nodes = sr.findall(".//materials/materialsItem")

            for material in material_nodes:
                billable_text = (
                    material.findtext("isBillable")
                    or material.findtext("billable")
                    or ""
                ).strip().lower()
                rows.append({
                    "id": material.findtext("materialId") or material.findtext("id"),
                    "itemId": material.findtext("itemId"),
                    "itemName": material.findtext("itemName"),
                    "description": material.findtext("itemDescription") or material.findtext("description"),
                    "quantity": material.findtext("itemQuantity") or material.findtext("quantity"),
                    "unitPrice": material.findtext("itemUnitPrice") or material.findtext("unitPrice"),
                    "total": material.findtext("totalPrice") or material.findtext("totalprice") or material.findtext("total"),
                    "isBillable": billable_text in {"1", "true", "yes", "y"},
                })

            return jsonify({
                "serviceRequestId": str(service_request_id),
                "materials": rows,
            })
        except (BlueFolderError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 502

    @app.get("/service-requests/<int:service_request_id>/materials/debug")
    def service_request_materials_debug(service_request_id):
        """Return direct fields present in each BlueFolder materialsItem."""
        try:
            client = client_factory()
            xml_response = client.service_requests.get_by_id(service_request_id)
            sr = xml_response.find(".//serviceRequest")
            if sr is None and xml_response.tag == "serviceRequest":
                sr = xml_response
            if sr is None:
                return jsonify({"error": "service request not found"}), 404

            material_nodes = sr.findall("./materials/materialsItem")
            if not material_nodes:
                material_nodes = sr.findall(".//materials/materialsItem")

            rows = []
            for material in material_nodes:
                fields = {}
                for child in material:
                    value = child.text if child.text is not None else ""
                    if child.tag in fields:
                        existing = fields[child.tag]
                        if not isinstance(existing, list):
                            fields[child.tag] = [existing]
                        fields[child.tag].append(value)
                    else:
                        fields[child.tag] = value
                rows.append(fields)

            return jsonify({"serviceRequestId": str(service_request_id), "materials": rows})
        except (BlueFolderError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 502

    @app.get("/assignments")
    def assignments():
        user_id = request.args.get("userId", type=int)
        day = request.args.get("date")
        start_date = request.args.get("startDate")
        end_date = request.args.get("endDate")

        if not user_id:
            return jsonify({"error": "userId is required and must be a positive integer"}), 400

        if day:
            try:
                parsed = date.fromisoformat(day)
            except ValueError:
                return jsonify({"error": "date must use YYYY-MM-DD"}), 400
            bf_day = parsed.strftime("%Y.%m.%d")
            start_date = f"{bf_day} 12:00 AM"
            end_date = f"{bf_day} 11:59 PM"
        elif not (start_date and end_date):
            return jsonify({"error": "provide date=YYYY-MM-DD or both startDate and endDate"}), 400

        try:
            client = client_factory()
            rows = client.assignments.list_for_user_range(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                date_range_type="scheduled",
            )
            return jsonify({
                "userId": user_id,
                "startDate": start_date,
                "endDate": end_date,
                "assignments": rows,
            })
        except (BlueFolderError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 502

    return app


app = create_app()
