"""Tests for announcements tool."""

from __future__ import annotations

import pytest

from canvas_cli.models import AuthContext
from canvas_cli.tools.announcements import (
    canvas_list_announcements,
    serialize_announcement,
)


@pytest.mark.integration
class TestCanvasListAnnouncements:
    """Integration tests for canvas_list_announcements tool."""

    def test_list_announcements_success(self, auth_context):
        """Test listing announcements with valid auth."""
        result = canvas_list_announcements(auth_context)

        assert result["ok"] is True
        assert result["tool"] == "canvas_list_announcements"
        assert "items" in result

    def test_list_announcements_for_specific_courses(self, auth_context, sample_course_id):
        """Test listing announcements for specific courses."""
        result = canvas_list_announcements(
            auth_context,
            course_ids=[sample_course_id],
        )

        assert result["ok"] is True
        # If items exist, they should be from the specified course
        for item in result["items"]:
            if item.get("course_id"):
                assert item["course_id"] == sample_course_id

    def test_list_announcements_with_date_filter(self, auth_context, sample_course_id):
        """Test listing announcements with date filter."""
        result = canvas_list_announcements(
            auth_context,
            course_ids=[sample_course_id],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        assert result["ok"] is True

    def test_list_announcements_pagination(self, auth_context):
        """Test listing announcements with pagination."""
        result = canvas_list_announcements(
            auth_context,
            page=1,
            page_size=10,
        )

        assert result["ok"] is True
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["page_size"] == 10

    def test_announcement_has_expected_fields(self, auth_context, sample_course_id):
        """Test that announcement response has expected fields."""
        result = canvas_list_announcements(
            auth_context,
            course_ids=[sample_course_id],
        )

        if result["items"]:
            announcement = result["items"][0]
            expected_fields = [
                "id",
                "title",
                "message",
                "posted_at",
            ]

            for field in expected_fields:
                assert field in announcement, f"Missing field: {field}"


@pytest.mark.integration
class TestAnnouncementsToolErrors:
    """Tests for announcements tool error handling."""

    def test_list_announcements_invalid_token(self):
        """Test listing announcements with invalid auth."""
        auth = AuthContext(
            canvas_base_url="https://canvas.instructure.com/api/v1",
            canvas_access_token="invalid_token",
        )
        result = canvas_list_announcements(auth)

        assert result["ok"] is False
        assert len(result["errors"]) > 0


class TestSerializeAnnouncement:
    """Unit tests for serialize_announcement function."""

    def test_serialize_announcement_basic(self):
        """Test serializing basic announcement."""
        class MockAnnouncement:
            id = 123
            title = "Important Announcement"
            message = "<p>Announcement content</p>"
            course_id = 456
            posted_at = "2024-01-15T10:00:00Z"
            created_at = "2024-01-15T10:00:00Z"
            updated_at = "2024-01-15T11:00:00Z"
            url = "https://example.com/announcement"
            html_url = "https://example.com/announcement"
            author = {"id": 1, "display_name": "Instructor"}
            read_state = "read"
            unread_count = 0
            discussion_subentry_count = 3
            published = True
            locked = False

        result = serialize_announcement(MockAnnouncement())

        assert result["id"] == 123
        assert result["title"] == "Important Announcement"
        assert result["course_id"] == 456
        assert result["discussion_subentry_count"] == 3
        assert result["author"]["display_name"] == "Instructor"

    def test_serialize_announcement_with_missing_author(self):
        """Test serializing announcement with missing author."""
        class MockAnnouncement:
            id = 123
            title = "Test"
            message = "Content"
            author = None

        result = serialize_announcement(MockAnnouncement())

        assert result["author"]["id"] is None
        assert result["author"]["display_name"] is None
