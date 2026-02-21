"""Announcements tool - canvas_list_announcements."""

from __future__ import annotations

from typing import Any

from canvasapi.exceptions import CanvasException

from ..canvas_client import CanvasClient
from ..models import AuthContext
from ..utils.normalize_time import normalize_canvas_time
from ..utils.pagination import build_tool_output


def serialize_announcement(announcement: Any) -> dict[str, Any]:
    """Serialize a Canvas Announcement to dict."""
    author = getattr(announcement, "author", {}) or {}
    return {
        "id": getattr(announcement, "id", None),
        "title": getattr(announcement, "title", None),
        "message": getattr(announcement, "message", None),
        "course_id": getattr(announcement, "course_id", None),
        "posted_at": normalize_canvas_time(getattr(announcement, "posted_at", None)),
        "created_at": normalize_canvas_time(getattr(announcement, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(announcement, "updated_at", None)),
        "url": getattr(announcement, "url", None),
        "html_url": getattr(announcement, "html_url", None),
        "author": {
            "id": author.get("id") if isinstance(author, dict) else None,
            "display_name": author.get("display_name") if isinstance(author, dict) else None,
            "avatar_image_url": author.get("avatar_image_url")
            if isinstance(author, dict)
            else None,
        },
        "read_state": getattr(announcement, "read_state", None),
        "unread_count": getattr(announcement, "unread_count", 0),
        "discussion_subentry_count": getattr(announcement, "discussion_subentry_count", 0),
        "delayed_post_at": normalize_canvas_time(
            getattr(announcement, "delayed_post_at", None)
        ),
        "published": getattr(announcement, "published", None),
        "locked": getattr(announcement, "locked", None),
    }


def canvas_list_announcements(
    auth: AuthContext,
    *,
    course_ids: list[int] | None = None,
    page: int = 1,
    page_size: int = 100,
    start_date: str | None = None,
    end_date: str | None = None,
    since: str | None = None,
) -> dict[str, Any]:
    """
    List announcements for one or more courses.

    Args:
        auth: Authentication context
        course_ids: List of course IDs to fetch announcements from
        page: Page number
        page_size: Items per page
        start_date: Start date filter (ISO format)
        end_date: End date filter (ISO format)
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with announcements
    """
    errors: list[str] = []

    try:
        client = CanvasClient(auth)
        canvas = client.client

        # If no course_ids specified, get all active courses first
        if not course_ids:
            user = client.get_current_user()
            courses = list(user.get_courses(enrollment_state=["active"]))
            course_ids = [c.id for c in courses]

        all_announcements: list[Any] = []

        # Fetch announcements for each course
        for course_id in course_ids:
            try:
                course = client.get_course(course_id)
                kwargs: dict[str, Any] = {}
                if start_date:
                    kwargs["start_date"] = start_date
                if end_date:
                    kwargs["end_date"] = end_date

                paginated = course.get_discussion_topics(only_announcements=True, **kwargs)
                announcements = list(paginated)
                all_announcements.extend(announcements)
            except CanvasException as e:
                errors.append(f"Error fetching announcements for course {course_id}: {e}")
                continue

        # Sort by posted_at descending
        all_announcements.sort(
            key=lambda a: getattr(a, "posted_at", None) or "",
            reverse=True,
        )

        # Filter by since if provided
        if since:
            from ..utils.normalize_time import is_after

            all_announcements = [
                a
                for a in all_announcements
                if is_after(getattr(a, "updated_at", None), since)
            ]

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        sliced = all_announcements[start_idx:end_idx]
        has_more = len(all_announcements) > end_idx

        serialized = [serialize_announcement(a) for a in sliced]

        return build_tool_output(
            tool="canvas_list_announcements",
            items=serialized,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_list_announcements",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_list_announcements",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
