"""Assignments tools - assignments, quizzes, submissions."""

from __future__ import annotations

from typing import Any

from canvasapi.exceptions import CanvasException

from ..canvas_client import CanvasClient
from ..models import AuthContext
from ..utils.normalize_time import normalize_canvas_time
from ..utils.pagination import build_tool_output


def serialize_assignment(assignment: Any) -> dict[str, Any]:
    """Serialize a Canvas Assignment to dict."""
    result = {
        "id": getattr(assignment, "id", None),
        "name": getattr(assignment, "name", None),
        "description": getattr(assignment, "description", None),
        "course_id": getattr(assignment, "course_id", None),
        "points_possible": getattr(assignment, "points_possible", None),
        "due_at": normalize_canvas_time(getattr(assignment, "due_at", None)),
        "lock_at": normalize_canvas_time(getattr(assignment, "lock_at", None)),
        "unlock_at": normalize_canvas_time(getattr(assignment, "unlock_at", None)),
        "workflow_state": getattr(assignment, "workflow_state", None),
        "assignment_group_id": getattr(assignment, "assignment_group_id", None),
        "grading_type": getattr(assignment, "grading_type", None),
        "submission_types": getattr(assignment, "submission_types", []),
        "has_submitted_submissions": getattr(assignment, "has_submitted_submissions", False),
        "has_overrides": getattr(assignment, "has_overrides", False),
        "html_url": getattr(assignment, "html_url", None),
        "created_at": normalize_canvas_time(getattr(assignment, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(assignment, "updated_at", None)),
        "published": getattr(assignment, "published", None),
        "unpublishable": getattr(assignment, "unpublishable", None),
    }

    # Include submission data if available
    submission = getattr(assignment, "submission", None)
    if submission:
        result["submission"] = {
            "id": getattr(submission, "id", None),
            "grade": getattr(submission, "grade", None),
            "score": getattr(submission, "score", None),
            "submitted_at": normalize_canvas_time(getattr(submission, "submitted_at", None)),
            "workflow_state": getattr(submission, "workflow_state", None),
            "late": getattr(submission, "late", False),
            "missing": getattr(submission, "missing", False),
        }

    return result


def serialize_quiz(quiz: Any) -> dict[str, Any]:
    """Serialize a Canvas Quiz to dict."""
    return {
        "id": getattr(quiz, "id", None),
        "title": getattr(quiz, "title", None),
        "description": getattr(quiz, "description", None),
        "quiz_type": getattr(quiz, "quiz_type", None),
        "course_id": getattr(quiz, "course_id", None),
        "points_possible": getattr(quiz, "points_possible", None),
        "due_at": normalize_canvas_time(getattr(quiz, "due_at", None)),
        "lock_at": normalize_canvas_time(getattr(quiz, "lock_at", None)),
        "unlock_at": normalize_canvas_time(getattr(quiz, "unlock_at", None)),
        "time_limit": getattr(quiz, "time_limit", None),
        "shuffle_answers": getattr(quiz, "shuffle_answers", None),
        "show_correct_answers": getattr(quiz, "show_correct_answers", None),
        "show_correct_answers_at": normalize_canvas_time(
            getattr(quiz, "show_correct_answers_at", None)
        ),
        "hide_correct_answers_at": normalize_canvas_time(
            getattr(quiz, "hide_correct_answers_at", None)
        ),
        "allowed_attempts": getattr(quiz, "allowed_attempts", None),
        "scoring_policy": getattr(quiz, "scoring_policy", None),
        "question_count": getattr(quiz, "question_count", None),
        "html_url": getattr(quiz, "html_url", None),
        "mobile_url": getattr(quiz, "mobile_url", None),
        "published": getattr(quiz, "published", None),
        "unpublishable": getattr(quiz, "unpublishable", None),
        "locked_for_user": getattr(quiz, "locked_for_user", None),
        "created_at": normalize_canvas_time(getattr(quiz, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(quiz, "updated_at", None)),
    }


def canvas_list_assignments(
    auth: AuthContext,
    *,
    course_id: int,
    page: int = 1,
    page_size: int = 100,
    include_submissions: bool = False,
    since: str | None = None,
) -> dict[str, Any]:
    """
    List assignments for a course.

    Args:
        auth: Authentication context
        course_id: Canvas course ID
        page: Page number
        page_size: Items per page
        include_submissions: Include submission data
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with assignments
    """
    errors: list[str] = []

    try:
        client = CanvasClient(auth)
        course = client.get_course(course_id)

        kwargs: dict[str, Any] = {}
        if include_submissions:
            kwargs["include"] = ["submission"]

        paginated = course.get_assignments(**kwargs)
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        # Filter by since if provided
        if since:
            from ..utils.normalize_time import is_after

            items = [
                item
                for item in items
                if is_after(getattr(item, "updated_at", None), since)
            ]

        assignments = [serialize_assignment(assignment) for assignment in items]

        return build_tool_output(
            tool="canvas_list_assignments",
            items=assignments,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_list_assignments",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_list_assignments",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )


def canvas_list_quizzes(
    auth: AuthContext,
    *,
    course_id: int,
    page: int = 1,
    page_size: int = 100,
    since: str | None = None,
) -> dict[str, Any]:
    """
    List quizzes for a course.

    Args:
        auth: Authentication context
        course_id: Canvas course ID
        page: Page number
        page_size: Items per page
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with quizzes
    """
    errors: list[str] = []

    try:
        client = CanvasClient(auth)
        course = client.get_course(course_id)

        paginated = course.get_quizzes()
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        # Filter by since if provided
        if since:
            from ..utils.normalize_time import is_after

            items = [
                item
                for item in items
                if is_after(getattr(item, "updated_at", None), since)
            ]

        quizzes = [serialize_quiz(quiz) for quiz in items]

        return build_tool_output(
            tool="canvas_list_quizzes",
            items=quizzes,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_list_quizzes",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_list_quizzes",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
