"""Tests for bundle tool."""

from __future__ import annotations

import pytest

from canvas_cli.models import AuthContext
from canvas_cli.tools.bundle import canvas_get_delta_bundle


@pytest.mark.integration
class TestCanvasGetDeltaBundle:
    """Integration tests for canvas_get_delta_bundle tool."""

    def test_get_delta_bundle_success(self, auth_context):
        """Test getting delta bundle with valid auth."""
        result = canvas_get_delta_bundle(auth_context)

        # Bundle may have errors from sub-tools, but should return valid structure
        assert "ok" in result
        assert result["tool"] == "canvas_get_delta_bundle"
        assert len(result["items"]) == 1

        bundle = result["items"][0]
        assert "profile" in bundle
        assert "courses" in bundle
        assert "todo_items" in bundle
        assert "upcoming_events" in bundle
        assert "calendar_events" in bundle
        assert "planner_items" in bundle
        assert "course_data" in bundle

    def test_get_delta_bundle_with_profile(self, auth_context):
        """Test that delta bundle includes profile."""
        result = canvas_get_delta_bundle(auth_context)

        bundle = result["items"][0]

        if bundle["profile"]:
            assert "id" in bundle["profile"]
            assert "name" in bundle["profile"]

    def test_get_delta_bundle_with_courses(self, auth_context):
        """Test that delta bundle includes courses."""
        result = canvas_get_delta_bundle(auth_context)

        bundle = result["items"][0]

        if bundle["courses"]:
            course = bundle["courses"][0]
            assert "id" in course
            assert "name" in course

    def test_get_delta_bundle_with_specific_courses(self, auth_context, sample_course_id):
        """Test getting delta bundle for specific courses."""
        result = canvas_get_delta_bundle(
            auth_context,
            course_ids=[sample_course_id],
        )

        # May have errors but structure should be valid
        assert "ok" in result
        bundle = result["items"][0]
        assert str(sample_course_id) in bundle["course_data"]

        course_data = bundle["course_data"][str(sample_course_id)]
        assert "assignments" in course_data
        assert "quizzes" in course_data
        assert "discussions" in course_data
        assert "announcements" in course_data

    def test_get_delta_bundle_with_since(self, auth_context, sample_course_id):
        """Test getting delta bundle with since parameter."""
        result = canvas_get_delta_bundle(
            auth_context,
            course_ids=[sample_course_id],
            since="2024-01-01T00:00:00Z",
        )

        # May have errors but structure should be valid
        assert "ok" in result
        assert "items" in result

    def test_bundle_course_data_structure(self, auth_context, sample_course_id):
        """Test that course data has expected structure."""
        result = canvas_get_delta_bundle(
            auth_context,
            course_ids=[sample_course_id],
        )

        bundle = result["items"][0]
        course_data = bundle["course_data"][str(sample_course_id)]

        # Check that all expected keys exist
        assert "assignments" in course_data
        assert "quizzes" in course_data
        assert "discussions" in course_data
        assert "announcements" in course_data

        # Check that they are lists
        assert isinstance(course_data["assignments"], list)
        assert isinstance(course_data["quizzes"], list)
        assert isinstance(course_data["discussions"], list)
        assert isinstance(course_data["announcements"], list)

    def test_bundle_schedule_data(self, auth_context):
        """Test that schedule data is included in bundle."""
        result = canvas_get_delta_bundle(auth_context)

        bundle = result["items"][0]

        # These should be lists (even if empty)
        assert isinstance(bundle["todo_items"], list)
        assert isinstance(bundle["upcoming_events"], list)
        assert isinstance(bundle["calendar_events"], list)
        assert isinstance(bundle["planner_items"], list)


@pytest.mark.integration
class TestBundleToolErrors:
    """Tests for bundle tool error handling."""

    def test_get_delta_bundle_invalid_token(self):
        """Test getting delta bundle with invalid auth."""
        auth = AuthContext(
            canvas_base_url="https://canvas.instructure.com/api/v1",
            canvas_access_token="invalid_token",
        )
        result = canvas_get_delta_bundle(auth)

        # Bundle collects errors from individual tool calls
        # but should still return ok=True with partial data if possible
        # or ok=False if all calls fail
        assert "ok" in result
        assert "items" in result

    def test_get_delta_bundle_invalid_course_id(self, auth_context):
        """Test getting delta bundle with invalid course ID."""
        result = canvas_get_delta_bundle(
            auth_context,
            course_ids=[999999999],
        )

        # Should return structure with errors
        assert "ok" in result
        assert "items" in result
        bundle = result["items"][0]

        # Course data should exist but may be empty or have errors
        assert "999999999" in bundle["course_data"]
