"""Pydantic models for Canvas CLI tools."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuthContext(BaseModel):
    """Authentication context for Canvas API."""

    canvas_base_url: str = Field(
        ...,
        description="Canvas instance base URL (e.g., https://canvas.instructure.com/api/v1)",
    )
    canvas_access_token: str = Field(
        ...,
        description="Canvas API access token",
    )


class PaginationParams(BaseModel):
    """Common pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(
        default=100, ge=1, le=100, description="Number of items per page"
    )


class ToolInput(BaseModel):
    """Base input for all Canvas tools."""

    auth: AuthContext
    since: str | None = Field(
        default=None, description="ISO timestamp for delta/incremental fetches"
    )


class PaginationInfo(BaseModel):
    """Pagination metadata in responses."""

    page: int
    page_size: int
    next_page: int | None = None
    total_count: int | None = None


class ToolOutput(BaseModel):
    """Base output for all Canvas tools."""

    ok: bool = True
    source: str = "canvas"
    tool: str
    items: list[dict[str, Any]] = Field(default_factory=list)
    pagination: PaginationInfo | None = None
    fetched_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )
    errors: list[str] = Field(default_factory=list)


# Tool-specific input models


class CourseIdInput(ToolInput):
    """Input for tools that require a course_id."""

    course_id: int = Field(..., description="Canvas course ID")


class ConversationIdInput(ToolInput):
    """Input for getting a single conversation."""

    conversation_id: int = Field(..., description="Canvas conversation ID")


class DiscussionTopicInput(CourseIdInput):
    """Input for discussion topic operations."""

    topic_id: int = Field(..., description="Canvas discussion topic ID")


class DiscussionEntryInput(DiscussionTopicInput):
    """Input for discussion entry operations."""

    entry_id: int = Field(..., description="Canvas discussion entry ID")


class ModuleIdInput(CourseIdInput):
    """Input for module operations."""

    module_id: int = Field(..., description="Canvas module ID")


class ListCoursesInput(ToolInput, PaginationParams):
    """Input for listing courses."""

    enrollment_state: str | None = Field(
        default=None, description="Filter by enrollment state (active, completed, etc.)"
    )


class ListAssignmentsInput(CourseIdInput, PaginationParams):
    """Input for listing assignments."""

    include_submissions: bool = Field(
        default=False, description="Include submission data"
    )


class ListQuizzesInput(CourseIdInput, PaginationParams):
    """Input for listing quizzes."""

    pass


class ListDiscussionTopicsInput(CourseIdInput, PaginationParams):
    """Input for listing discussion topics."""

    only_announcements: bool = Field(
        default=False, description="Filter to only announcements"
    )


class ListAnnouncementsInput(ToolInput, PaginationParams):
    """Input for listing announcements."""

    course_ids: list[int] | None = Field(
        default=None, description="List of course IDs to fetch announcements from"
    )


class ListConversationsInput(ToolInput, PaginationParams):
    """Input for listing conversations."""

    scope: str | None = Field(
        default=None, description="Filter scope (unread, starred, archived, etc.)"
    )


class ListCalendarEventsInput(ToolInput, PaginationParams):
    """Input for listing calendar events."""

    start_date: str | None = Field(default=None, description="Start date (ISO format)")
    end_date: str | None = Field(default=None, description="End date (ISO format)")
    context_codes: list[str] | None = Field(
        default=None, description="Context codes to filter (e.g., ['course_123'])"
    )


class ListModulesInput(CourseIdInput, PaginationParams):
    """Input for listing modules."""

    pass


class ListModuleItemsInput(ModuleIdInput, PaginationParams):
    """Input for listing module items."""

    pass


class ListPagesInput(CourseIdInput, PaginationParams):
    """Input for listing pages."""

    pass


class ListFilesInput(CourseIdInput, PaginationParams):
    """Input for listing files."""

    pass


class DeltaBundleInput(ToolInput):
    """Input for delta bundle aggregator."""

    course_ids: list[int] | None = Field(
        default=None, description="List of course IDs to include in bundle"
    )
