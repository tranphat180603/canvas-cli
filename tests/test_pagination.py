"""Tests for pagination utilities."""

from __future__ import annotations

import pytest

from canvas_cli.utils.pagination import (
    build_pagination_result,
    build_tool_output,
    slice_items,
)


class TestBuildPaginationResult:
    """Tests for build_pagination_result function."""

    def test_basic_pagination(self):
        """Test basic pagination result."""
        result = build_pagination_result(
            items=[1, 2, 3],
            page=1,
            page_size=10,
            has_more=True,
        )

        assert result["page"] == 1
        assert result["page_size"] == 10
        assert result["next_page"] == 2

    def test_no_more_pages(self):
        """Test pagination result with no more pages."""
        result = build_pagination_result(
            items=[1, 2, 3],
            page=5,
            page_size=10,
            has_more=False,
        )

        assert result["page"] == 5
        assert result["next_page"] is None

    def test_with_total_count(self):
        """Test pagination result with total count."""
        result = build_pagination_result(
            items=[1, 2, 3],
            page=1,
            page_size=10,
            has_more=True,
            total_count=100,
        )

        assert result["total_count"] == 100


class TestBuildToolOutput:
    """Tests for build_tool_output function."""

    def test_successful_output(self):
        """Test building successful tool output."""
        result = build_tool_output(
            tool="test_tool",
            items=[{"id": 1}, {"id": 2}],
            page=1,
            page_size=10,
            has_more=False,
        )

        assert result["ok"] is True
        assert result["tool"] == "test_tool"
        assert result["source"] == "canvas"
        assert len(result["items"]) == 2
        assert len(result["errors"]) == 0
        assert "fetched_at" in result
        assert "pagination" in result

    def test_output_with_errors(self):
        """Test building tool output with errors."""
        result = build_tool_output(
            tool="test_tool",
            items=[],
            page=1,
            page_size=10,
            has_more=False,
            errors=["Something went wrong"],
        )

        assert result["ok"] is False
        assert len(result["errors"]) == 1

    def test_output_with_total_count(self):
        """Test building tool output with total count."""
        result = build_tool_output(
            tool="test_tool",
            items=[{"id": 1}],
            page=1,
            page_size=10,
            has_more=True,
            total_count=100,
        )

        assert result["pagination"]["total_count"] == 100


class TestSliceItems:
    """Tests for slice_items function."""

    def test_first_page(self):
        """Test slicing first page."""
        items = list(range(1, 101))  # 1 to 100
        sliced, has_more = slice_items(items, page=1, page_size=10)

        assert len(sliced) == 10
        assert sliced[0] == 1
        assert sliced[-1] == 10
        assert has_more is True

    def test_middle_page(self):
        """Test slicing middle page."""
        items = list(range(1, 101))  # 1 to 100
        sliced, has_more = slice_items(items, page=5, page_size=10)

        assert len(sliced) == 10
        assert sliced[0] == 41
        assert sliced[-1] == 50
        assert has_more is True

    def test_last_page(self):
        """Test slicing last page."""
        items = list(range(1, 101))  # 1 to 100
        sliced, has_more = slice_items(items, page=10, page_size=10)

        assert len(sliced) == 10
        assert sliced[0] == 91
        assert sliced[-1] == 100
        assert has_more is False

    def test_partial_last_page(self):
        """Test slicing partial last page."""
        items = list(range(1, 96))  # 1 to 95
        sliced, has_more = slice_items(items, page=10, page_size=10)

        assert len(sliced) == 5
        assert sliced[0] == 91
        assert sliced[-1] == 95
        assert has_more is False

    def test_empty_items(self):
        """Test slicing empty list."""
        sliced, has_more = slice_items([], page=1, page_size=10)

        assert len(sliced) == 0
        assert has_more is False

    def test_page_beyond_range(self):
        """Test slicing page beyond range."""
        items = list(range(1, 11))  # 1 to 10
        sliced, has_more = slice_items(items, page=5, page_size=10)

        assert len(sliced) == 0
        assert has_more is False

    def test_custom_page_size(self):
        """Test slicing with custom page size."""
        items = list(range(1, 51))  # 1 to 50
        sliced, has_more = slice_items(items, page=2, page_size=20)

        assert len(sliced) == 20
        assert sliced[0] == 21
        assert sliced[-1] == 40
        assert has_more is True


@pytest.mark.integration
class TestRealPagination:
    """Integration tests for pagination with real Canvas data."""

    def test_courses_pagination(self, auth_context):
        """Test that courses pagination works correctly."""
        from canvas_cli.tools.courses import canvas_list_courses

        # Get first page
        result1 = canvas_list_courses(auth_context, page=1, page_size=5)

        assert result1["ok"] is True
        assert result1["pagination"]["page"] == 1
        assert result1["pagination"]["page_size"] == 5

        # If there are enough courses, test second page
        if result1["pagination"]["next_page"]:
            result2 = canvas_list_courses(auth_context, page=2, page_size=5)

            assert result2["ok"] is True
            assert result2["pagination"]["page"] == 2

            # Items should be different (unless duplicates in data)
            ids1 = {c["id"] for c in result1["items"]}
            ids2 = {c["id"] for c in result2["items"]}

            # Should not have exact same set
            # (This could fail if user has very few courses)
            if len(ids1) == 5 and len(ids2) > 0:
                assert ids1 != ids2
