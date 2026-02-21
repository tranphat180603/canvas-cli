"""Canvas CLI tools package."""

from .announcements import canvas_list_announcements
from .assignments import canvas_list_assignments, canvas_list_quizzes
from .bundle import canvas_get_delta_bundle
from .conversations import canvas_get_conversation, canvas_list_conversations
from .courses import canvas_list_courses
from .discussions import (
    canvas_get_discussion_entries,
    canvas_get_discussion_replies,
    canvas_list_discussion_topics,
)
from .profile import canvas_get_profile
from .schedule import (
    canvas_get_calendar_events,
    canvas_get_planner_items,
    canvas_get_todo_items,
    canvas_get_upcoming_events,
)
from .structure import (
    canvas_list_files,
    canvas_list_module_items,
    canvas_list_modules,
    canvas_list_pages,
)

__all__ = [
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

# Tool registry for MCP server
TOOL_REGISTRY = {
    "canvas_get_profile": {
        "function": canvas_get_profile,
        "description": "Get the current user's Canvas profile.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {
                    "type": "object",
                    "description": "Authentication context with canvas_base_url and canvas_access_token",
                },
            },
            "required": ["auth"],
        },
    },
    "canvas_list_courses": {
        "function": canvas_list_courses,
        "description": "List courses for the current user.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "enrollment_state": {"type": "string", "description": "Filter by enrollment state"},
                "since": {"type": "string", "description": "ISO timestamp for delta fetch"},
            },
            "required": ["auth"],
        },
    },
    "canvas_get_todo_items": {
        "function": canvas_get_todo_items,
        "description": "Get todo items for the current user.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "since": {"type": "string"},
            },
            "required": ["auth"],
        },
    },
    "canvas_get_upcoming_events": {
        "function": canvas_get_upcoming_events,
        "description": "Get upcoming events for the current user.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "since": {"type": "string"},
            },
            "required": ["auth"],
        },
    },
    "canvas_get_calendar_events": {
        "function": canvas_get_calendar_events,
        "description": "Get calendar events for the current user.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "context_codes": {"type": "array", "items": {"type": "string"}},
                "since": {"type": "string"},
            },
            "required": ["auth"],
        },
    },
    "canvas_get_planner_items": {
        "function": canvas_get_planner_items,
        "description": "Get planner items for the current user.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "context_codes": {"type": "array", "items": {"type": "string"}},
                "since": {"type": "string"},
            },
            "required": ["auth"],
        },
    },
    "canvas_list_assignments": {
        "function": canvas_list_assignments,
        "description": "List assignments for a course.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "course_id": {"type": "integer"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "include_submissions": {"type": "boolean", "default": False},
                "since": {"type": "string"},
            },
            "required": ["auth", "course_id"],
        },
    },
    "canvas_list_quizzes": {
        "function": canvas_list_quizzes,
        "description": "List quizzes for a course.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "course_id": {"type": "integer"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "since": {"type": "string"},
            },
            "required": ["auth", "course_id"],
        },
    },
    "canvas_list_discussion_topics": {
        "function": canvas_list_discussion_topics,
        "description": "List discussion topics for a course.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "course_id": {"type": "integer"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "only_announcements": {"type": "boolean", "default": False},
                "since": {"type": "string"},
            },
            "required": ["auth", "course_id"],
        },
    },
    "canvas_get_discussion_entries": {
        "function": canvas_get_discussion_entries,
        "description": "Get entries for a discussion topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "course_id": {"type": "integer"},
                "topic_id": {"type": "integer"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "since": {"type": "string"},
            },
            "required": ["auth", "course_id", "topic_id"],
        },
    },
    "canvas_get_discussion_replies": {
        "function": canvas_get_discussion_replies,
        "description": "Get replies for a discussion entry.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "course_id": {"type": "integer"},
                "topic_id": {"type": "integer"},
                "entry_id": {"type": "integer"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "since": {"type": "string"},
            },
            "required": ["auth", "course_id", "topic_id", "entry_id"],
        },
    },
    "canvas_list_conversations": {
        "function": canvas_list_conversations,
        "description": "List conversations (inbox) for the current user.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "scope": {"type": "string"},
                "since": {"type": "string"},
            },
            "required": ["auth"],
        },
    },
    "canvas_get_conversation": {
        "function": canvas_get_conversation,
        "description": "Get a single conversation with messages.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "conversation_id": {"type": "integer"},
                "since": {"type": "string"},
            },
            "required": ["auth", "conversation_id"],
        },
    },
    "canvas_list_announcements": {
        "function": canvas_list_announcements,
        "description": "List announcements for courses.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "course_ids": {"type": "array", "items": {"type": "integer"}},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "since": {"type": "string"},
            },
            "required": ["auth"],
        },
    },
    "canvas_list_modules": {
        "function": canvas_list_modules,
        "description": "List modules for a course.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "course_id": {"type": "integer"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "since": {"type": "string"},
            },
            "required": ["auth", "course_id"],
        },
    },
    "canvas_list_module_items": {
        "function": canvas_list_module_items,
        "description": "List items in a module.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "course_id": {"type": "integer"},
                "module_id": {"type": "integer"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "since": {"type": "string"},
            },
            "required": ["auth", "course_id", "module_id"],
        },
    },
    "canvas_list_pages": {
        "function": canvas_list_pages,
        "description": "List pages for a course.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "course_id": {"type": "integer"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "since": {"type": "string"},
            },
            "required": ["auth", "course_id"],
        },
    },
    "canvas_list_files": {
        "function": canvas_list_files,
        "description": "List files for a course.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "course_id": {"type": "integer"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 100},
                "since": {"type": "string"},
            },
            "required": ["auth", "course_id"],
        },
    },
    "canvas_get_delta_bundle": {
        "function": canvas_get_delta_bundle,
        "description": "Get a comprehensive bundle of Canvas data for syncing. Aggregates profile, courses, schedule items, and course-specific data.",
        "parameters": {
            "type": "object",
            "properties": {
                "auth": {"type": "object"},
                "course_ids": {"type": "array", "items": {"type": "integer"}},
                "since": {"type": "string", "description": "ISO timestamp for delta fetch"},
            },
            "required": ["auth"],
        },
    },
}
