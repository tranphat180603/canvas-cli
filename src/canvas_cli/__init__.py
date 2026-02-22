"""Canvas CLI - MCP server exposing Canvas LMS data as tools."""

__version__ = "0.1.0"

from .models import AuthContext
from .tools import (
    TOOL_REGISTRY,
    canvas_get_conversation,
    canvas_get_delta_bundle,
    canvas_get_discussion_entries,
    canvas_get_discussion_replies,
    canvas_get_planner_items,
    canvas_get_profile,
    canvas_get_todo_items,
    canvas_get_upcoming_events,
    canvas_get_calendar_events,
    canvas_list_announcements,
    canvas_list_assignments,
    canvas_list_assignment_groups,
    canvas_list_conversations,
    canvas_list_courses,
    canvas_list_discussion_topics,
    canvas_list_files,
    canvas_list_module_items,
    canvas_list_modules,
    canvas_list_pages,
    canvas_list_quizzes,
)

__all__ = [
    "AuthContext",
    "TOOL_REGISTRY",
    # Profile
    "canvas_get_profile",
    # Courses
    "canvas_list_courses",
    # Schedule
    "canvas_get_todo_items",
    "canvas_get_upcoming_events",
    "canvas_get_calendar_events",
    "canvas_get_planner_items",
    # Assignments
    "canvas_list_assignments",
    "canvas_list_quizzes",
    "canvas_list_assignment_groups",
    # Discussions
    "canvas_list_discussion_topics",
    "canvas_get_discussion_entries",
    "canvas_get_discussion_replies",
    # Conversations
    "canvas_list_conversations",
    "canvas_get_conversation",
    # Announcements
    "canvas_list_announcements",
    # Structure
    "canvas_list_modules",
    "canvas_list_module_items",
    "canvas_list_pages",
    "canvas_list_files",
    # Bundle
    "canvas_get_delta_bundle",
]
