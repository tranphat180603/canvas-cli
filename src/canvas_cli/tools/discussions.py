"""Discussion tools - topics, entries, replies."""

from typing import Any, Dict, List, Optional

from canvasapi.exceptions import CanvasException

from ..canvas_client import CanvasClient
from ..utils.normalize_time import normalize_canvas_time
from ..utils.pagination import build_tool_output
from .auth import resolve_auth


def serialize_discussion_topic(topic: Any) -> Dict[str, Any]:
    """Serialize a Canvas Discussion Topic to dict."""
    author = getattr(topic, "author", {}) or {}
    return {
        "id": getattr(topic, "id", None),
        "title": getattr(topic, "title", None),
        "message": getattr(topic, "message", None),
        "course_id": getattr(topic, "course_id", None),
        "discussion_type": getattr(topic, "discussion_type", None),
        "discussion_subentry_count": getattr(topic, "discussion_subentry_count", 0),
        "published": getattr(topic, "published", None),
        "locked": getattr(topic, "locked", None),
        "pinned": getattr(topic, "pinned", None),
        "position": getattr(topic, "position", None),
        "url": getattr(topic, "url", None),
        "html_url": getattr(topic, "html_url", None),
        "posted_at": normalize_canvas_time(getattr(topic, "posted_at", None)),
        "created_at": normalize_canvas_time(getattr(topic, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(topic, "updated_at", None)),
        "last_reply_at": normalize_canvas_time(getattr(topic, "last_reply_at", None)),
        "author": {
            "id": author.get("id") if isinstance(author, dict) else None,
            "display_name": author.get("display_name") if isinstance(author, dict) else None,
            "avatar_image_url": author.get("avatar_image_url")
            if isinstance(author, dict)
            else None,
        },
        "is_announcement": getattr(topic, "is_announcement", False),
        "has_more_replies": getattr(topic, "has_more_replies", False),
    }


def serialize_discussion_entry(entry: Any) -> Dict[str, Any]:
    """Serialize a Canvas Discussion Entry to dict."""
    return {
        "id": getattr(entry, "id", None),
        "user_id": getattr(entry, "user_id", None),
        "user_name": getattr(entry, "user_name", None),
        "message": getattr(entry, "message", None),
        "created_at": normalize_canvas_time(getattr(entry, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(entry, "updated_at", None)),
        "parent_id": getattr(entry, "parent_id", None),
        "read_state": getattr(entry, "read_state", None),
        "forced_read_state": getattr(entry, "forced_read_state", None),
        "discussion_subentry_count": getattr(entry, "discussion_subentry_count", 0),
        "has_more_replies": getattr(entry, "has_more_replies", False),
    }


def serialize_discussion_reply(reply: Any) -> Dict[str, Any]:
    """Serialize a Canvas Discussion Reply to dict."""
    # Replies are similar to entries
    return serialize_discussion_entry(reply)


def canvas_list_discussion_topics(
    auth: Optional[Dict[str, Any]] = None,
    *,
    course_id: int,
    page: int = 1,
    page_size: int = 100,
    only_announcements: bool = False,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List discussion topics for a course.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        course_id: Canvas course ID
        page: Page number
        page_size: Items per page
        only_announcements: Filter to only announcements
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with discussion topics
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)
        course = client.get_course(course_id)

        kwargs: Dict[str, Any] = {}
        if only_announcements:
            kwargs["only_announcements"] = True

        paginated = course.get_discussion_topics(**kwargs)
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        # Filter by since if provided
        if since:
            from ..utils.normalize_time import is_after

            items = [
                item
                for item in items
                if is_after(getattr(item, "updated_at", None), since)
            ]

        topics = [serialize_discussion_topic(topic) for topic in items]

        return build_tool_output(
            tool="canvas_list_discussion_topics",
            items=topics,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_list_discussion_topics",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_list_discussion_topics",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )


def canvas_get_discussion_entries(
    auth: Optional[Dict[str, Any]] = None,
    *,
    course_id: int,
    topic_id: int,
    page: int = 1,
    page_size: int = 100,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get entries for a discussion topic.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        course_id: Canvas course ID
        topic_id: Canvas discussion topic ID
        page: Page number
        page_size: Items per page
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with discussion entries
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)
        course = client.get_course(course_id)

        # Get the topic first
        topic = course.get_discussion_topic(topic_id)

        paginated = topic.get_topic_entries()
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        # Filter by since if provided
        if since:
            from ..utils.normalize_time import is_after

            items = [
                item
                for item in items
                if is_after(getattr(item, "updated_at", None), since)
            ]

        entries = [serialize_discussion_entry(entry) for entry in items]

        return build_tool_output(
            tool="canvas_get_discussion_entries",
            items=entries,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_get_discussion_entries",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_get_discussion_entries",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )


def canvas_get_discussion_replies(
    auth: Optional[Dict[str, Any]] = None,
    *,
    course_id: int,
    topic_id: int,
    entry_id: int,
    page: int = 1,
    page_size: int = 100,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get replies for a discussion entry.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        course_id: Canvas course ID
        topic_id: Canvas discussion topic ID
        entry_id: Canvas discussion entry ID
        page: Page number
        page_size: Items per page
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with discussion replies
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)
        course = client.get_course(course_id)

        # Get the topic
        topic = course.get_discussion_topic(topic_id)

        # Get the entry
        entry = topic.get_topic_entries(entry_id)  # type: ignore

        # Get replies
        paginated = entry.get_replies()
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        # Filter by since if provided
        if since:
            from ..utils.normalize_time import is_after

            items = [
                item
                for item in items
                if is_after(getattr(item, "updated_at", None), since)
            ]

        replies = [serialize_discussion_reply(reply) for reply in items]

        return build_tool_output(
            tool="canvas_get_discussion_replies",
            items=replies,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_get_discussion_replies",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_get_discussion_replies",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
