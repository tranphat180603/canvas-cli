"""Authentication and Canvas client handling."""

from __future__ import annotations

from typing import TYPE_CHECKING

from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

from .models import AuthContext

if TYPE_CHECKING:
    pass


class AuthError(Exception):
    """Raised when authentication fails."""

    pass


def get_canvas_client(auth: AuthContext) -> Canvas:
    """
    Create and return a Canvas API client.

    Args:
        auth: Authentication context with base URL and access token

    Returns:
        Canvas client instance

    Raises:
        AuthError: If the auth context is invalid
    """
    if not auth.canvas_base_url:
        raise AuthError("Canvas base URL is required")

    if not auth.canvas_access_token:
        raise AuthError("Canvas access token is required")

    # Normalize the base URL - canvasapi expects NO /api/v1 suffix
    # It adds /api/v1 internally
    base_url = auth.canvas_base_url.rstrip("/")
    if base_url.endswith("/api/v1"):
        base_url = base_url[:-7]  # Remove /api/v1

    try:
        client = Canvas(base_url, auth.canvas_access_token)
        return client
    except Exception as e:
        raise AuthError(f"Failed to create Canvas client: {e}") from e


def validate_auth(auth: AuthContext) -> None:
    """
    Validate authentication by making a test API call.

    Args:
        auth: Authentication context to validate

    Raises:
        AuthError: If authentication fails
    """
    try:
        client = get_canvas_client(auth)
        # Make a simple API call to verify credentials
        client.get_current_user()
    except CanvasException as e:
        raise AuthError(f"Canvas authentication failed: {e}") from e
    except Exception as e:
        raise AuthError(f"Authentication validation error: {e}") from e
