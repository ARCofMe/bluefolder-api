"""Small JSON/HTTP facade for Power Platform and other integrations."""

import os
from datetime import date, datetime

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
