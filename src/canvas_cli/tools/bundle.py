"""Bundle tool - delta bundle aggregator."""

from __future__ import annotations

from typing import Any

from ..models import AuthContext
from ..utils.pagination import build_tool_output
from .announcements import canvas_list_announcements
from .assignments import canvas_list_assignments, canvas_list_quizzes
from .courses import canvas_list_courses
from .discussions import canvas_list_discussion_topics
from .profile import canvas_get_profile
from .schedule import (
    canvas_get_calendar_events,
    canvas_get_planner_items,
    canvas_get_todo_items,
    canvas_get_upcoming_events,
)


def canvas_get_delta_bundle(
    auth: AuthContext,
    *,
    course_ids: list[int] | None = None,
    since: str | None = None,
) -> dict[str, Any]:
    """
    Get a comprehensive bundle of Canvas data for syncing.

    This aggregates multiple tools to provide a complete snapshot of
    relevant Canvas data. Useful for initial sync or delta updates.

    Args:
        auth: Authentication context
        course_ids: List of course IDs to include. If None, uses all active courses.
        since: ISO timestamp for delta fetch. Only items updated after this time
               will be included.

    Returns:
        Tool output with bundled data from multiple sources:
        - profile: Current user profile
        - courses: List of courses
        - todo_items: Todo items
        - upcoming_events: Upcoming events
        - calendar_events: Calendar events
        - planner_items: Planner items
        - For each course:
          - assignments: Course assignments
          - quizzes: Course quizzes
          - discussions: Discussion topics (non-announcements)
          - announcements: Course announcements
    """
    errors: list[str] = []
    bundle: dict[str, Any] = {
        "profile": None,
        "courses": [],
        "todo_items": [],
        "upcoming_events": [],
        "calendar_events": [],
        "planner_items": [],
        "course_data": {},
    }

    # 1. Get profile
    profile_result = canvas_get_profile(auth)
    if profile_result.get("ok") and profile_result.get("items"):
        bundle["profile"] = profile_result["items"][0]
    if profile_result.get("errors"):
        errors.extend(profile_result["errors"])

    # 2. Get courses
    courses_result = canvas_list_courses(
        auth, enrollment_state="active", page=1, page_size=100, since=since
    )
    if courses_result.get("ok"):
        bundle["courses"] = courses_result.get("items", [])
    if courses_result.get("errors"):
        errors.extend(courses_result["errors"])

    # Determine course IDs to process
    if course_ids is None:
        course_ids = [c["id"] for c in bundle["courses"] if c.get("id")]

    # 3. Get schedule items
    todo_result = canvas_get_todo_items(auth, page=1, page_size=100, since=since)
    if todo_result.get("ok"):
        bundle["todo_items"] = todo_result.get("items", [])
    if todo_result.get("errors"):
        errors.extend(todo_result["errors"])

    upcoming_result = canvas_get_upcoming_events(auth, page=1, page_size=100, since=since)
    if upcoming_result.get("ok"):
        bundle["upcoming_events"] = upcoming_result.get("items", [])
    if upcoming_result.get("errors"):
        errors.extend(upcoming_result["errors"])

    calendar_result = canvas_get_calendar_events(auth, page=1, page_size=100, since=since)
    if calendar_result.get("ok"):
        bundle["calendar_events"] = calendar_result.get("items", [])
    if calendar_result.get("errors"):
        errors.extend(calendar_result["errors"])

    planner_result = canvas_get_planner_items(auth, page=1, page_size=100, since=since)
    if planner_result.get("ok"):
        bundle["planner_items"] = planner_result.get("items", [])
    if planner_result.get("errors"):
        errors.extend(planner_result["errors"])

    # 4. Get course-specific data
    for course_id in course_ids:
        course_data: dict[str, Any] = {
            "assignments": [],
            "quizzes": [],
            "discussions": [],
            "announcements": [],
        }

        # Assignments
        assignments_result = canvas_list_assignments(
            auth, course_id=course_id, page=1, page_size=100, include_submissions=True, since=since
        )
        if assignments_result.get("ok"):
            course_data["assignments"] = assignments_result.get("items", [])
        if assignments_result.get("errors"):
            errors.extend(assignments_result["errors"])

        # Quizzes
        quizzes_result = canvas_list_quizzes(
            auth, course_id=course_id, page=1, page_size=100, since=since
        )
        if quizzes_result.get("ok"):
            course_data["quizzes"] = quizzes_result.get("items", [])
        if quizzes_result.get("errors"):
            errors.extend(quizzes_result["errors"])

        # Discussions (not announcements)
        discussions_result = canvas_list_discussion_topics(
            auth, course_id=course_id, page=1, page_size=100, only_announcements=False, since=since
        )
        if discussions_result.get("ok"):
            course_data["discussions"] = discussions_result.get("items", [])
        if discussions_result.get("errors"):
            errors.extend(discussions_result["errors"])

        # Announcements
        announcements_result = canvas_list_announcements(
            auth, course_ids=[course_id], page=1, page_size=50, since=since
        )
        if announcements_result.get("ok"):
            course_data["announcements"] = announcements_result.get("items", [])
        if announcements_result.get("errors"):
            errors.extend(announcements_result["errors"])

        bundle["course_data"][str(course_id)] = course_data

    return build_tool_output(
        tool="canvas_get_delta_bundle",
        items=[bundle],
        page=1,
        page_size=1,
        has_more=False,
        errors=errors,
    )
