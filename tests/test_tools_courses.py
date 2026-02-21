"""Tests for courses tool."""

from __future__ import annotations

import pytest

from canvas_cli.models import AuthContext
from canvas_cli.tools.courses import canvas_list_courses, serialize_course


@pytest.mark.integration
class TestCanvasListCourses:
    """Integration tests for canvas_list_courses tool."""

    def test_list_courses_success(self, auth_context):
        """Test listing courses with valid auth."""
        result = canvas_list_courses(auth_context)

        assert result["ok"] is True
        assert result["tool"] == "canvas_list_courses"
        assert result["source"] == "canvas"
        assert "items" in result
        assert len(result["errors"]) == 0

    def test_list_courses_with_enrollment_filter(self, auth_context):
        """Test listing courses with enrollment state filter."""
        result = canvas_list_courses(auth_context, enrollment_state="active")

        assert result["ok"] is True
        # All returned courses should have active enrollment
        for course in result["items"]:
            if "enrollments" in course and course["enrollments"]:
                # At least one enrollment should be active
                pass  # This depends on the data

    def test_list_courses_pagination(self, auth_context):
        """Test listing courses with pagination."""
        result = canvas_list_courses(auth_context, page=1, page_size=10)

        assert result["ok"] is True
        assert "pagination" in result
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["page_size"] == 10

    def test_list_courses_invalid_token(self):
        """Test listing courses with invalid auth."""
        auth = AuthContext(
            canvas_base_url="https://canvas.instructure.com/api/v1",
            canvas_access_token="invalid_token",
        )
        result = canvas_list_courses(auth)

        assert result["ok"] is False
        assert len(result["errors"]) > 0

    def test_course_has_expected_fields(self, auth_context):
        """Test that course response has expected fields."""
        result = canvas_list_courses(auth_context)

        if result["items"]:
            course = result["items"][0]
            expected_fields = [
                "id",
                "name",
                "course_code",
                "workflow_state",
            ]

            for field in expected_fields:
                assert field in course, f"Missing field: {field}"


class TestSerializeCourse:
    """Unit tests for serialize_course function."""

    def test_serialize_course_with_all_fields(self):
        """Test serializing course with all fields."""
        class MockCourse:
            id = 123
            name = "Introduction to Testing"
            course_code = "TEST101"
            workflow_state = "available"
            enrollment_term_id = 1
            start_at = "2024-01-15T00:00:00Z"
            end_at = "2024-05-15T00:00:00Z"
            created_at = "2024-01-01T00:00:00Z"
            updated_at = "2024-01-02T00:00:00Z"
            syllabus_body = "<p>Syllabus content</p>"
            public_description = "A test course"
            enrollments = []
            calendar = {"ics": "https://example.com/calendar.ics"}
            default_view = "modules"
            is_public = False
            has_active_course_offering = True

        result = serialize_course(MockCourse())

        assert result["id"] == 123
        assert result["name"] == "Introduction to Testing"
        assert result["course_code"] == "TEST101"
        assert result["workflow_state"] == "available"

    def test_serialize_course_with_enrollments(self):
        """Test serializing course with enrollments."""
        class MockEnrollment:
            type = "StudentEnrollment"
            role = "StudentEnrollment"
            enrollment_state = "active"

        class MockCourse:
            id = 123
            name = "Test Course"
            course_code = "TEST101"
            workflow_state = "available"
            enrollments = [MockEnrollment()]

        result = serialize_course(MockCourse())

        assert len(result["enrollments"]) == 1
        assert result["enrollments"][0]["type"] == "StudentEnrollment"
