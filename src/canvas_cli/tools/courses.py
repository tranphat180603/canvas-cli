"""Courses tool - canvas_list_courses."""

from typing import Any, Dict, List, Optional

from canvasapi.exceptions import CanvasException

from ..canvas_client import CanvasClient
from ..utils.normalize_time import normalize_canvas_time
from ..utils.pagination import build_tool_output, slice_items
from .auth import resolve_auth


def serialize_course(course: Any) -> Dict[str, Any]:
    """Serialize a Canvas Course to dict."""
    return {
        "id": getattr(course, "id", None),
        "name": getattr(course, "name", None),
        "course_code": getattr(course, "course_code", None),
        "workflow_state": getattr(course, "workflow_state", None),
        "enrollment_term_id": getattr(course, "enrollment_term_id", None),
        "start_at": normalize_canvas_time(getattr(course, "start_at", None)),
        "end_at": normalize_canvas_time(getattr(course, "end_at", None)),
        "created_at": normalize_canvas_time(getattr(course, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(course, "updated_at", None)),
        "syllabus_body": getattr(course, "syllabus_body", None),
        "public_description": getattr(course, "public_description", None),
        "enrollments": [
            {
                "type": getattr(e, "type", None),
                "role": getattr(e, "role", None),
                "enrollment_state": getattr(e, "enrollment_state", None),
            }
            for e in (getattr(course, "enrollments", []) or [])
        ],
        "calendar": getattr(course, "calendar", None),
        "default_view": getattr(course, "default_view", None),
        "is_public": getattr(course, "is_public", None),
        "has_active_course_offering": getattr(course, "has_active_course_offering", None),
    }


def canvas_list_courses(
    auth: Optional[Dict[str, Any]] = None,
    *,
    page: int = 1,
    page_size: int = 100,
    enrollment_state: Optional[str] = None,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List courses for the current user.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        page: Page number (1-indexed)
        page_size: Number of items per page
        enrollment_state: Filter by enrollment state (active, completed, etc.)
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with course data
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)
        user = client.get_current_user()

        # Build kwargs for get_courses
        kwargs: Dict[str, Any] = {}
        if enrollment_state:
            kwargs["enrollment_state"] = [enrollment_state]

        # Get paginated list
        paginated = user.get_courses(**kwargs)
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        # Filter by since if provided
        if since:
            from ..utils.normalize_time import is_after

            items = [
                item
                for item in items
                if is_after(getattr(item, "updated_at", None), since)
            ]

        # Serialize courses
        courses = [serialize_course(course) for course in items]

        return build_tool_output(
            tool="canvas_list_courses",
            items=courses,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_list_courses",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_list_courses",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
