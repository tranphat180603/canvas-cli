"""Profile tool - canvas_get_profile."""

from __future__ import annotations

from typing import Any

from canvasapi.exceptions import CanvasException

from ..canvas_client import CanvasClient
from ..models import AuthContext, ToolOutput
from ..utils.normalize_time import normalize_canvas_time, to_iso
from ..utils.pagination import build_tool_output


def serialize_profile(user: Any) -> dict[str, Any]:
    """Serialize a Canvas User/profile to dict."""
    return {
        "id": getattr(user, "id", None),
        "name": getattr(user, "name", None),
        "short_name": getattr(user, "short_name", None),
        "login_id": getattr(user, "login_id", None),
        "email": getattr(user, "email", None),
        "locale": getattr(user, "locale", None),
        "time_zone": getattr(user, "time_zone", None),
        "bio": getattr(user, "bio", None),
        "avatar_url": getattr(user, "avatar_url", None),
        "created_at": normalize_canvas_time(getattr(user, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(user, "updated_at", None)),
    }


def canvas_get_profile(auth: AuthContext) -> dict[str, Any]:
    """
    Get the current user's Canvas profile.

    Args:
        auth: Authentication context

    Returns:
        Tool output with profile data
    """
    errors: list[str] = []

    try:
        client = CanvasClient(auth)
        user = client.get_current_user()

        profile_data = serialize_profile(user)

        return build_tool_output(
            tool="canvas_get_profile",
            items=[profile_data],
            page=1,
            page_size=1,
            has_more=False,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_get_profile",
            items=[],
            page=1,
            page_size=1,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_get_profile",
            items=[],
            page=1,
            page_size=1,
            has_more=False,
            errors=errors,
        )
