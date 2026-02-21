"""Tests for assignments tools."""

from __future__ import annotations

import pytest

from canvas_cli.models import AuthContext
from canvas_cli.tools.assignments import (
    canvas_list_assignments,
    canvas_list_quizzes,
    serialize_assignment,
    serialize_quiz,
)


@pytest.mark.integration
class TestCanvasListAssignments:
    """Integration tests for canvas_list_assignments tool."""

    def test_list_assignments_success(self, auth_context, sample_course_id):
        """Test listing assignments with valid auth."""
        result = canvas_list_assignments(auth_context, course_id=sample_course_id)

        assert result["ok"] is True
        assert result["tool"] == "canvas_list_assignments"
        assert "items" in result

    def test_list_assignments_with_submissions(self, auth_context, sample_course_id):
        """Test listing assignments with submissions."""
        result = canvas_list_assignments(
            auth_context,
            course_id=sample_course_id,
            include_submissions=True,
        )

        assert result["ok"] is True

    def test_list_assignments_pagination(self, auth_context, sample_course_id):
        """Test listing assignments with pagination."""
        result = canvas_list_assignments(
            auth_context,
            course_id=sample_course_id,
            page=1,
            page_size=10,
        )

        assert result["ok"] is True
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["page_size"] == 10

    def test_assignment_has_expected_fields(self, auth_context, sample_course_id):
        """Test that assignment response has expected fields."""
        result = canvas_list_assignments(auth_context, course_id=sample_course_id)

        if result["items"]:
            assignment = result["items"][0]
            expected_fields = [
                "id",
                "name",
                "course_id",
                "points_possible",
                "workflow_state",
            ]

            for field in expected_fields:
                assert field in assignment, f"Missing field: {field}"


@pytest.mark.integration
class TestCanvasListQuizzes:
    """Integration tests for canvas_list_quizzes tool."""

    def test_list_quizzes_success(self, auth_context, sample_course_id):
        """Test listing quizzes with valid auth."""
        result = canvas_list_quizzes(auth_context, course_id=sample_course_id)

        assert result["ok"] is True
        assert result["tool"] == "canvas_list_quizzes"
        assert "items" in result

    def test_list_quizzes_pagination(self, auth_context, sample_course_id):
        """Test listing quizzes with pagination."""
        result = canvas_list_quizzes(
            auth_context,
            course_id=sample_course_id,
            page=1,
            page_size=10,
        )

        assert result["ok"] is True


@pytest.mark.integration
class TestAssignmentsToolErrors:
    """Tests for assignments tool error handling."""

    def test_list_assignments_invalid_course(self, auth_context):
        """Test listing assignments with invalid course ID."""
        result = canvas_list_assignments(auth_context, course_id=999999999)

        # Should return an error for non-existent course
        assert result["ok"] is False
        assert len(result["errors"]) > 0

    def test_list_quizzes_invalid_course(self, auth_context):
        """Test listing quizzes with invalid course ID."""
        result = canvas_list_quizzes(auth_context, course_id=999999999)

        assert result["ok"] is False


class TestSerializeAssignment:
    """Unit tests for serialize_assignment function."""

    def test_serialize_assignment_basic(self):
        """Test serializing basic assignment."""
        class MockAssignment:
            id = 123
            name = "Test Assignment"
            description = "Test description"
            course_id = 456
            points_possible = 100
            due_at = "2024-02-01T23:59:59Z"
            workflow_state = "published"
            html_url = "https://example.com/assignment"

        result = serialize_assignment(MockAssignment())

        assert result["id"] == 123
        assert result["name"] == "Test Assignment"
        assert result["points_possible"] == 100
        assert result["course_id"] == 456


class TestSerializeQuiz:
    """Unit tests for serialize_quiz function."""

    def test_serialize_quiz_basic(self):
        """Test serializing basic quiz."""
        class MockQuiz:
            id = 123
            title = "Test Quiz"
            description = "Test quiz description"
            course_id = 456
            points_possible = 50
            quiz_type = "assignment"
            due_at = "2024-02-01T23:59:59Z"
            time_limit = 60
            allowed_attempts = 3
            question_count = 10
            html_url = "https://example.com/quiz"

        result = serialize_quiz(MockQuiz())

        assert result["id"] == 123
        assert result["title"] == "Test Quiz"
        assert result["time_limit"] == 60
        assert result["allowed_attempts"] == 3
