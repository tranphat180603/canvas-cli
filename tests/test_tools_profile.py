"""Tests for profile tool."""

from __future__ import annotations

import pytest

from canvas_cli.models import AuthContext
from canvas_cli.tools.profile import canvas_get_profile, serialize_profile


@pytest.mark.integration
class TestCanvasGetProfile:
    """Integration tests for canvas_get_profile tool."""

    def test_get_profile_success(self, auth_context):
        """Test getting profile with valid auth."""
        result = canvas_get_profile(auth_context)

        assert result["ok"] is True
        assert result["tool"] == "canvas_get_profile"
        assert result["source"] == "canvas"
        assert len(result["items"]) == 1
        assert len(result["errors"]) == 0

        profile = result["items"][0]
        assert "id" in profile
        assert "name" in profile
        assert profile["id"] is not None

    def test_get_profile_invalid_token(self):
        """Test getting profile with invalid auth."""
        auth = AuthContext(
            canvas_base_url="https://canvas.instructure.com/api/v1",
            canvas_access_token="invalid_token",
        )
        result = canvas_get_profile(auth)

        assert result["ok"] is False
        assert len(result["errors"]) > 0

    def test_profile_has_expected_fields(self, auth_context):
        """Test that profile response has expected fields."""
        result = canvas_get_profile(auth_context)

        profile = result["items"][0]
        expected_fields = [
            "id",
            "name",
            "short_name",
            "login_id",
            "email",
            "locale",
            "time_zone",
            "avatar_url",
            "created_at",
        ]

        for field in expected_fields:
            assert field in profile, f"Missing field: {field}"


class TestSerializeProfile:
    """Unit tests for serialize_profile function."""

    def test_serialize_profile_with_all_fields(self):
        """Test serializing profile with all fields."""
        class MockUser:
            id = 123
            name = "Test User"
            short_name = "Test"
            login_id = "testuser"
            email = "test@example.com"
            locale = "en"
            time_zone = "America/New_York"
            bio = "Test bio"
            avatar_url = "https://example.com/avatar.png"
            created_at = "2024-01-01T00:00:00Z"
            updated_at = "2024-01-02T00:00:00Z"

        result = serialize_profile(MockUser())

        assert result["id"] == 123
        assert result["name"] == "Test User"
        assert result["short_name"] == "Test"
        assert result["login_id"] == "testuser"
        assert result["email"] == "test@example.com"
        assert result["locale"] == "en"
        assert result["time_zone"] == "America/New_York"
        assert result["bio"] == "Test bio"
        assert result["avatar_url"] == "https://example.com/avatar.png"

    def test_serialize_profile_with_missing_fields(self):
        """Test serializing profile with missing fields."""
        class MockUser:
            id = 123
            name = "Test User"

        result = serialize_profile(MockUser())

        assert result["id"] == 123
        assert result["name"] == "Test User"
        assert result["email"] is None
        assert result["locale"] is None
