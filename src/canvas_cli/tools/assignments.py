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
    # Note: submission can be a dict (from include=['submission']) or an object
    submission = getattr(assignment, "submission", None)
    if submission:
        if isinstance(submission, dict):
            # Handle dict format (from include=['submission'])
            result["submission"] = {
                "id": submission.get("id"),
                "grade": submission.get("grade"),
                "score": submission.get("score"),
                "submitted_at": normalize_canvas_time(submission.get("submitted_at")),
                "workflow_state": submission.get("workflow_state"),
                "late": submission.get("late", False),
                "missing": submission.get("missing", False),
            }
        else:
            # Handle object format
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

    Note: Some Canvas instances don't allow direct quiz listing.
    This tool will try the direct API first, then fall back to
    extracting quizzes from modules.

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

        all_quizzes = []

        # Try direct API first
        try:
            paginated = course.get_quizzes()
            items, _ = CanvasClient.extract_paginated_list(paginated, 1, 1000)
            all_quizzes = [serialize_quiz(q) for q in items]
        except Exception:
            # Direct API failed, use fallback
            errors.append("Direct quizzes API unavailable, using module fallback")

        # Fallback: Extract quizzes from modules if direct API failed
        if not all_quizzes:
            modules = list(course.get_modules())

            for module in modules:
                try:
                    module_items = list(module.get_module_items())
                    for item in module_items:
                        if getattr(item, 'type', None) == 'Quiz':
                            quiz_id = getattr(item, 'content_id', None)
                            if quiz_id:
                                try:
                                    q = course.get_quiz(quiz_id)
                                    all_quizzes.append(serialize_quiz(q))
                                except Exception:
                                    all_quizzes.append({
                                        "id": quiz_id,
                                        "title": getattr(item, 'title', None),
                                        "course_id": course_id,
                                    })
                except Exception:
                    continue

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_quizzes = all_quizzes[start_idx:end_idx]
        has_more = len(all_quizzes) > end_idx

        return build_tool_output(
            tool="canvas_list_quizzes",
            items=paginated_quizzes,
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


def canvas_list_assignment_groups(
    auth: AuthContext,
    *,
    course_id: int,
) -> dict[str, Any]:
    """
    List assignment groups with weights for a course.

    Assignment groups determine how much each category of assignments
    contributes to the final grade.

    Args:
        auth: Authentication context
        course_id: Canvas course ID

    Returns:
        Tool output with assignment groups including:
        - id: Group ID
        - name: Group name
        - weight: Percentage weight (0-100)
        - points_possible: Total points in group
    """
    errors: list[str] = []

    try:
        client = CanvasClient(auth)
        course = client.get_course(course_id)

        groups = list(course.get_assignment_groups())

        items = []
        total_weight = 0

        for g in groups:
            weight = getattr(g, "group_weight", 0) or 0
            total_weight += weight

            items.append({
                "id": getattr(g, "id", None),
                "name": getattr(g, "name", None),
                "weight": weight,
                "points_possible": getattr(g, "points_possible", None),
                "assigns_assignments": getattr(g, "assigns_assignments", None),
            })

        return {
            "ok": True,
            "source": "canvas",
            "tool": "canvas_list_assignment_groups",
            "items": items,
            "total_weight": total_weight,
            "errors": errors,
        }

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return {
            "ok": False,
            "source": "canvas",
            "tool": "canvas_list_assignment_groups",
            "items": [],
            "total_weight": 0,
            "errors": errors,
        }
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return {
            "ok": False,
            "source": "canvas",
            "tool": "canvas_list_assignment_groups",
            "items": [],
            "total_weight": 0,
            "errors": errors,
        }
