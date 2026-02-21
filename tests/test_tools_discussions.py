"""Tests for discussion tools."""

from __future__ import annotations

import pytest

from canvas_cli.models import AuthContext
from canvas_cli.tools.discussions import (
    canvas_list_discussion_topics,
    canvas_get_discussion_entries,
    canvas_get_discussion_replies,
    serialize_discussion_topic,
)


@pytest.mark.integration
class TestCanvasListDiscussionTopics:
    """Integration tests for canvas_list_discussion_topics tool."""

    def test_list_discussion_topics_success(self, auth_context, sample_course_id):
        """Test listing discussion topics with valid auth."""
        result = canvas_list_discussion_topics(auth_context, course_id=sample_course_id)

        assert result["ok"] is True
        assert result["tool"] == "canvas_list_discussion_topics"
        assert "items" in result

    def test_list_discussion_topics_announcements_only(self, auth_context, sample_course_id):
        """Test listing only announcements."""
        result = canvas_list_discussion_topics(
            auth_context,
            course_id=sample_course_id,
            only_announcements=True,
        )

        assert result["ok"] is True
        # If items exist, they should be announcements
        for item in result["items"]:
            assert item.get("is_announcement", False) is True

    def test_list_discussion_topics_pagination(self, auth_context, sample_course_id):
        """Test listing discussion topics with pagination."""
        result = canvas_list_discussion_topics(
            auth_context,
            course_id=sample_course_id,
            page=1,
            page_size=10,
        )

        assert result["ok"] is True
        assert result["pagination"]["page"] == 1

    def test_discussion_topic_has_expected_fields(self, auth_context, sample_course_id):
        """Test that discussion topic response has expected fields."""
        result = canvas_list_discussion_topics(auth_context, course_id=sample_course_id)

        if result["items"]:
            topic = result["items"][0]
            expected_fields = [
                "id",
                "title",
                "course_id",
                "url",
                "created_at",
            ]

            for field in expected_fields:
                assert field in topic, f"Missing field: {field}"


@pytest.mark.integration
class TestCanvasGetDiscussionEntries:
    """Integration tests for canvas_get_discussion_entries tool."""

    def test_get_discussion_entries_success(self, auth_context, sample_course_id):
        """Test getting discussion entries."""
        # First get a topic
        topics_result = canvas_list_discussion_topics(
            auth_context,
            course_id=sample_course_id,
        )

        if not topics_result["items"]:
            pytest.skip("No discussion topics available for testing")

        topic_id = topics_result["items"][0]["id"]

        result = canvas_get_discussion_entries(
            auth_context,
            course_id=sample_course_id,
            topic_id=topic_id,
        )

        assert result["ok"] is True
        assert result["tool"] == "canvas_get_discussion_entries"
        assert "items" in result


@pytest.mark.integration
class TestCanvasGetDiscussionReplies:
    """Integration tests for canvas_get_discussion_replies tool."""

    def test_get_discussion_replies_requires_valid_entry(self, auth_context, sample_course_id):
        """Test getting discussion replies requires valid entry."""
        # First get a topic
        topics_result = canvas_list_discussion_topics(
            auth_context,
            course_id=sample_course_id,
        )

        if not topics_result["items"]:
            pytest.skip("No discussion topics available for testing")

        topic_id = topics_result["items"][0]["id"]

        # Try with an invalid entry ID
        result = canvas_get_discussion_replies(
            auth_context,
            course_id=sample_course_id,
            topic_id=topic_id,
            entry_id=999999999,
        )

        # Should return error for invalid entry
        assert result["ok"] is False or len(result["errors"]) > 0


@pytest.mark.integration
class TestDiscussionsToolErrors:
    """Tests for discussions tool error handling."""

    def test_list_discussion_topics_invalid_course(self, auth_context):
        """Test listing discussion topics with invalid course ID."""
        result = canvas_list_discussion_topics(auth_context, course_id=999999999)

        assert result["ok"] is False
        assert len(result["errors"]) > 0


class TestSerializeDiscussionTopic:
    """Unit tests for serialize_discussion_topic function."""

    def test_serialize_topic_basic(self):
        """Test serializing basic discussion topic."""
        class MockTopic:
            id = 123
            title = "Test Discussion"
            message = "<p>Discussion content</p>"
            course_id = 456
            discussion_type = "threaded"
            discussion_subentry_count = 5
            published = True
            locked = False
            url = "https://example.com/discussion"
            html_url = "https://example.com/discussion"
            posted_at = "2024-01-15T10:00:00Z"
            created_at = "2024-01-15T10:00:00Z"
            updated_at = "2024-01-15T11:00:00Z"
            author = {"id": 1, "display_name": "Test User"}
            is_announcement = False

        result = serialize_discussion_topic(MockTopic())

        assert result["id"] == 123
        assert result["title"] == "Test Discussion"
        assert result["discussion_subentry_count"] == 5
        assert result["is_announcement"] is False
        assert result["author"]["display_name"] == "Test User"
