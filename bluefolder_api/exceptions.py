"""Typed exception hierarchy for BlueFolder API failures."""


class BlueFolderError(RuntimeError):
    """Base class for BlueFolder client failures."""


class BlueFolderRequestError(BlueFolderError):
    """Raised when BlueFolder returns an HTTP or transport-level error."""

    def __init__(self, message: str, *, status_code: int | None = None, url: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.url = url


class BlueFolderAuthError(BlueFolderRequestError):
    """Raised when BlueFolder rejects API credentials."""


class BlueFolderRateLimitError(BlueFolderRequestError):
    """Raised when BlueFolder asks the caller to slow down."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        url: str | None = None,
        retry_after: float | None = None,
    ):
        super().__init__(message, status_code=status_code, url=url)
        self.retry_after = retry_after


class BlueFolderNotFoundError(BlueFolderRequestError):
    """Raised when a requested BlueFolder resource or endpoint is missing."""


class BlueFolderUnsupportedEndpointError(BlueFolderNotFoundError):
    """Raised when a tenant does not expose an endpoint."""


class BlueFolderInvalidResponseError(BlueFolderError):
    """Raised when BlueFolder returns malformed or unexpected payloads."""

