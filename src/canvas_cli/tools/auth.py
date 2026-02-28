"""Auth resolution utilities for Canvas CLI tools."""

import os
from typing import Union

from ..models import AuthContext


def resolve_auth(auth: Union[dict, AuthContext, None]) -> AuthContext:
    """Resolve auth from dict, AuthContext, or environment variables.

    Args:
        auth: Dict with canvas_base_url/canvasApiUrl and canvas_access_token/canvasApiKey,
              or an AuthContext object, or None to use env vars

    Returns:
        AuthContext with resolved credentials

    Raises:
        ValueError: If no auth provided and no env vars set
    """
    # If already an AuthContext, return it directly
    if isinstance(auth, AuthContext):
        return auth

    if auth:
        return AuthContext(
            canvas_base_url=auth.get("canvas_base_url") or auth.get("canvasApiUrl"),
            canvas_access_token=auth.get("canvas_access_token") or auth.get("canvasApiKey"),
        )
    # Fallback to environment variables
    url = os.getenv("CANVAS_API_URL")
    token = os.getenv("CANVAS_API_KEY")
    if not url or not token:
        raise ValueError(
            "No auth provided. Pass auth dict with canvas_base_url and canvas_access_token, "
            "or set CANVAS_API_URL and CANVAS_API_KEY environment variables."
        )
    return AuthContext(canvas_base_url=url, canvas_access_token=token)
