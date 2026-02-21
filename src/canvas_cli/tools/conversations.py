"""Conversation tools - inbox messages."""

from __future__ import annotations

from typing import Any

from canvasapi.exceptions import CanvasException

from ..canvas_client import CanvasClient
from ..models import AuthContext
from ..utils.normalize_time import normalize_canvas_time
from ..utils.pagination import build_tool_output


def serialize_conversation(convo: Any) -> dict[str, Any]:
    """Serialize a Canvas Conversation to dict."""
    return {
        "id": getattr(convo, "id", None),
        "subject": getattr(convo, "subject", None),
        "workflow_state": getattr(convo, "workflow_state", None),
        "last_message": getattr(convo, "last_message", None),
        "last_message_at": normalize_canvas_time(getattr(convo, "last_message_at", None)),
        "message_count": getattr(convo, "message_count", 0),
        "participants": [
            {
                "id": p.get("id") if isinstance(p, dict) else getattr(p, "id", None),
                "name": p.get("name") if isinstance(p, dict) else getattr(p, "name", None),
            }
            for p in (getattr(convo, "participants", []) or [])
        ],
        "starred": getattr(convo, "starred", False),
        "subscribed": getattr(convo, "subscribed", True),
        "audience": getattr(convo, "audience", []),
        "context_code": getattr(convo, "context_code", None),
        "context_name": getattr(convo, "context_name", None),
        "url": getattr(convo, "url", None),
        "created_at": normalize_canvas_time(getattr(convo, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(convo, "updated_at", None)),
    }


def serialize_conversation_message(msg: Any) -> dict[str, Any]:
    """Serialize a Canvas Conversation Message to dict."""
    return {
        "id": getattr(msg, "id", None),
        "body": getattr(msg, "body", None),
        "author_id": getattr(msg, "author_id", None),
        "author_name": getattr(msg, "author_name", None),
        "conversation_id": getattr(msg, "conversation_id", None),
        "created_at": normalize_canvas_time(getattr(msg, "created_at", None)),
        "generated": getattr(msg, "generated", False),
        "media_comment": getattr(msg, "media_comment", None),
        "forwarded_messages": getattr(msg, "forwarded_messages", []),
        "attachments": getattr(msg, "attachments", []),
        "participating_user_ids": getattr(msg, "participating_user_ids", []),
    }


def canvas_list_conversations(
    auth: AuthContext,
    *,
    page: int = 1,
    page_size: int = 100,
    scope: str | None = None,
    since: str | None = None,
) -> dict[str, Any]:
    """
    List conversations (inbox) for the current user.

    Args:
        auth: Authentication context
        page: Page number
        page_size: Items per page
        scope: Filter scope (unread, starred, archived, etc.)
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with conversations
    """
    errors: list[str] = []

    try:
        client = CanvasClient(auth)
        canvas = client.client

        kwargs: dict[str, Any] = {}
        if scope:
            kwargs["scope"] = scope

        paginated = canvas.get_conversations(**kwargs)
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        # Filter by since if provided
        if since:
            from ..utils.normalize_time import is_after

            items = [
                item
                for item in items
                if is_after(getattr(item, "updated_at", None), since)
            ]

        convos = [serialize_conversation(convo) for convo in items]

        return build_tool_output(
            tool="canvas_list_conversations",
            items=convos,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_list_conversations",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_list_conversations",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )


def canvas_get_conversation(
    auth: AuthContext,
    *,
    conversation_id: int,
    since: str | None = None,
) -> dict[str, Any]:
    """
    Get a single conversation with messages.

    Args:
        auth: Authentication context
        conversation_id: Canvas conversation ID
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with conversation details and messages
    """
    errors: list[str] = []

    try:
        client = CanvasClient(auth)
        canvas = client.client

        convo = canvas.get_conversation(conversation_id, include=["messages"])

        convo_data = serialize_conversation(convo)

        # Add messages
        messages = getattr(convo, "messages", []) or []
        if since:
            from ..utils.normalize_time import is_after

            messages = [
                msg
                for msg in messages
                if is_after(getattr(msg, "created_at", None), since)
            ]

        convo_data["messages"] = [serialize_conversation_message(msg) for msg in messages]

        return build_tool_output(
            tool="canvas_get_conversation",
            items=[convo_data],
            page=1,
            page_size=1,
            has_more=False,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_get_conversation",
            items=[],
            page=1,
            page_size=1,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_get_conversation",
            items=[],
            page=1,
            page_size=1,
            has_more=False,
            errors=errors,
        )
