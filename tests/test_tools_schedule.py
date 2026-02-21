"""Tests for schedule tools."""

from __future__ import annotations

import pytest

from canvas_cli.models import AuthContext
from canvas_cli.tools.schedule import (
    canvas_get_todo_items,
    canvas_get_upcoming_events,
    canvas_get_calendar_events,
    canvas_get_planner_items,
)


@pytest.mark.integration
class TestCanvasGetTodoItems:
    """Integration tests for canvas_get_todo_items tool."""

    def test_get_todo_items_success(self, auth_context):
        """Test getting todo items with valid auth."""
        result = canvas_get_todo_items(auth_context)

        # May fail if no todo items or permissions, but should return valid structure
        assert "ok" in result
        assert result["tool"] == "canvas_get_todo_items"
        assert "items" in result
        assert "errors" in result

    def test_get_todo_items_pagination(self, auth_context):
        """Test getting todo items with pagination."""
        result = canvas_get_todo_items(auth_context, page=1, page_size=10)

        # May fail if no todo items, but pagination structure should exist
        assert "pagination" in result
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["page_size"] == 10


@pytest.mark.integration
class TestCanvasGetUpcomingEvents:
    """Integration tests for canvas_get_upcoming_events tool."""

    def test_get_upcoming_events_success(self, auth_context):
        """Test getting upcoming events with valid auth."""
        result = canvas_get_upcoming_events(auth_context)

        # May fail if no upcoming events, but should return valid structure
        assert "ok" in result
        assert result["tool"] == "canvas_get_upcoming_events"
        assert "items" in result
        assert "errors" in result


@pytest.mark.integration
class TestCanvasGetCalendarEvents:
    """Integration tests for canvas_get_calendar_events tool."""

    def test_get_calendar_events_success(self, auth_context):
        """Test getting calendar events with valid auth."""
        result = canvas_get_calendar_events(auth_context)

        assert result["ok"] is True
        assert result["tool"] == "canvas_get_calendar_events"
        assert "items" in result

    def test_get_calendar_events_with_date_filter(self, auth_context):
        """Test getting calendar events with date filter."""
        result = canvas_get_calendar_events(
            auth_context,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        assert result["ok"] is True


@pytest.mark.integration
class TestCanvasGetPlannerItems:
    """Integration tests for canvas_get_planner_items tool."""

    def test_get_planner_items_success(self, auth_context):
        """Test getting planner items with valid auth."""
        result = canvas_get_planner_items(auth_context)

        # Planner may not be available on all Canvas instances
        # so we just check the response structure
        assert "ok" in result
        assert result["tool"] == "canvas_get_planner_items"
        assert "items" in result

    def test_get_planner_items_with_date_filter(self, auth_context):
        """Test getting planner items with date filter."""
        result = canvas_get_planner_items(
            auth_context,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        assert "ok" in result


@pytest.mark.integration
class TestScheduleToolErrors:
    """Tests for schedule tool error handling."""

    def test_todo_items_invalid_token(self):
        """Test getting todo items with invalid auth."""
        auth = AuthContext(
            canvas_base_url="https://canvas.instructure.com/api/v1",
            canvas_access_token="invalid_token",
        )
        result = canvas_get_todo_items(auth)

        assert result["ok"] is False
        assert len(result["errors"]) > 0
