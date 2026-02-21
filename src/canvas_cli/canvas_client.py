"""Canvas API client wrapper with common utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from canvasapi import Canvas
from canvasapi.paginated_list import PaginatedList

from .auth import get_canvas_client
from .models import AuthContext

if TYPE_CHECKING:
    pass

T = TypeVar("T")


class CanvasClient:
    """Wrapper around Canvas API client with utilities."""

    def __init__(self, auth: AuthContext) -> None:
        """Initialize with auth context."""
        self._auth = auth
        self._client: Canvas | None = None

    @property
    def client(self) -> Canvas:
        """Get the Canvas client, creating if needed."""
        if self._client is None:
            self._client = get_canvas_client(self._auth)
        return self._client

    @property
    def base_url(self) -> str:
        """Get the base URL for raw HTTP requests (includes /api/v1)."""
        url = self._auth.canvas_base_url.rstrip("/")
        if not url.endswith("/api/v1"):
            url = url + "/api/v1"
        return url

    @property
    def access_token(self) -> str:
        """Get the access token."""
        return self._auth.canvas_access_token

    def get_current_user(self):
        """Get the current authenticated user."""
        return self.client.get_current_user()

    def get_course(self, course_id: int):
        """Get a specific course by ID."""
        return self.client.get_course(course_id)

    @staticmethod
    def extract_paginated_list(
        paginated: PaginatedList, page: int = 1, page_size: int = 100
    ) -> tuple[list[Any], bool]:
        """
        Extract items from a PaginatedList with pagination.

        Args:
            paginated: Canvas PaginatedList object
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (items list, has_more boolean)
        """
        items = []
        has_more = False

        # PaginatedList doesn't have native pagination, so we iterate
        # and collect items manually
        try:
            # Get all items up to the page we need plus one extra
            # to check if there are more
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size + 1  # +1 to check for more

            all_items = []
            for i, item in enumerate(paginated):
                all_items.append(item)
                if i >= end_idx:
                    break

            # Extract the page
            items = all_items[start_idx:start_idx + page_size]

            # Check if there are more items
            has_more = len(all_items) > start_idx + page_size

        except Exception:
            # If pagination fails, return empty
            pass

        return items, has_more
