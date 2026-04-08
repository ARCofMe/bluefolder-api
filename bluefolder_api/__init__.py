"""Python client wrapper for the BlueFolder API domains."""

from .exceptions import (
    BlueFolderAuthError,
    BlueFolderError,
    BlueFolderInvalidResponseError,
    BlueFolderNotFoundError,
    BlueFolderRateLimitError,
    BlueFolderRequestError,
    BlueFolderUnsupportedEndpointError,
)

__all__ = [
    "BlueFolderError",
    "BlueFolderRequestError",
    "BlueFolderAuthError",
    "BlueFolderRateLimitError",
    "BlueFolderNotFoundError",
    "BlueFolderUnsupportedEndpointError",
    "BlueFolderInvalidResponseError",
]
