"""Tests for Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from canvas_cli.models import (
    AuthContext,
    PaginationInfo,
    PaginationParams,
    ToolInput,
    ToolOutput,
    ListCoursesInput,
    CourseIdInput,
)


class TestAuthContext:
    """Tests for AuthContext model."""

    def test_valid_auth_context(self):
        """Test creating valid AuthContext."""
        auth = AuthContext(
            canvas_base_url="https://canvas.example.com/api/v1",
            canvas_access_token="test_token_123",
        )
        assert auth.canvas_base_url == "https://canvas.example.com/api/v1"
        assert auth.canvas_access_token == "test_token_123"

    def test_auth_context_requires_fields(self):
        """Test that AuthContext requires both fields."""
        with pytest.raises(ValidationError):
            AuthContext()

        with pytest.raises(ValidationError):
            AuthContext(canvas_base_url="https://canvas.example.com")

        with pytest.raises(ValidationError):
            AuthContext(canvas_access_token="token")


class TestPaginationParams:
    """Tests for PaginationParams model."""

    def test_default_pagination(self):
        """Test default pagination values."""
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 100

    def test_custom_pagination(self):
        """Test custom pagination values."""
        params = PaginationParams(page=2, page_size=50)
        assert params.page == 2
        assert params.page_size == 50

    def test_page_minimum(self):
        """Test page minimum value."""
        with pytest.raises(ValidationError):
            PaginationParams(page=0)

    def test_page_size_limits(self):
        """Test page_size limits."""
        with pytest.raises(ValidationError):
            PaginationParams(page_size=0)

        with pytest.raises(ValidationError):
            PaginationParams(page_size=101)


class TestToolInput:
    """Tests for ToolInput model."""

    def test_valid_tool_input(self):
        """Test creating valid ToolInput."""
        auth = AuthContext(
            canvas_base_url="https://canvas.example.com/api/v1",
            canvas_access_token="test_token",
        )
        tool_input = ToolInput(auth=auth)
        assert tool_input.auth == auth
        assert tool_input.since is None

    def test_tool_input_with_since(self):
        """Test ToolInput with since parameter."""
        auth = AuthContext(
            canvas_base_url="https://canvas.example.com/api/v1",
            canvas_access_token="test_token",
        )
        tool_input = ToolInput(auth=auth, since="2024-01-01T00:00:00Z")
        assert tool_input.since == "2024-01-01T00:00:00Z"


class TestToolOutput:
    """Tests for ToolOutput model."""

    def test_successful_output(self):
        """Test creating successful ToolOutput."""
        output = ToolOutput(
            tool="test_tool",
            items=[{"id": 1, "name": "Test"}],
        )
        assert output.ok is True
        assert output.source == "canvas"
        assert output.tool == "test_tool"
        assert len(output.items) == 1
        assert len(output.errors) == 0
        assert output.fetched_at is not None

    def test_error_output(self):
        """Test creating error ToolOutput."""
        output = ToolOutput(
            ok=False,
            tool="test_tool",
            items=[],
            errors=["Something went wrong"],
        )
        assert output.ok is False
        assert len(output.errors) == 1

    def test_output_with_pagination(self):
        """Test ToolOutput with pagination info."""
        pagination = PaginationInfo(page=1, page_size=100, next_page=2, total_count=500)
        output = ToolOutput(
            tool="test_tool",
            items=[{"id": 1}],
            pagination=pagination,
        )
        assert output.pagination is not None
        assert output.pagination.page == 1
        assert output.pagination.next_page == 2


class TestListCoursesInput:
    """Tests for ListCoursesInput model."""

    def test_valid_list_courses_input(self):
        """Test creating valid ListCoursesInput."""
        auth = AuthContext(
            canvas_base_url="https://canvas.example.com/api/v1",
            canvas_access_token="test_token",
        )
        input_data = ListCoursesInput(
            auth=auth,
            page=1,
            page_size=50,
            enrollment_state="active",
        )
        assert input_data.auth == auth
        assert input_data.page == 1
        assert input_data.page_size == 50
        assert input_data.enrollment_state == "active"


class TestCourseIdInput:
    """Tests for CourseIdInput model."""

    def test_valid_course_id_input(self):
        """Test creating valid CourseIdInput."""
        auth = AuthContext(
            canvas_base_url="https://canvas.example.com/api/v1",
            canvas_access_token="test_token",
        )
        input_data = CourseIdInput(auth=auth, course_id=12345)
        assert input_data.course_id == 12345

    def test_course_id_required(self):
        """Test that course_id is required."""
        auth = AuthContext(
            canvas_base_url="https://canvas.example.com/api/v1",
            canvas_access_token="test_token",
        )
        with pytest.raises(ValidationError):
            CourseIdInput(auth=auth)
