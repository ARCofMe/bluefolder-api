"""Development entry point for the ARCoM BlueFolder JSON facade."""

import os

from bluefolder_api.web_api import app


if __name__ == "__main__":
    app.run(
        host=os.getenv("ARCOM_WRAPPER_HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        debug=False,
    )
