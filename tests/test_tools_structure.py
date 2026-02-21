"""Tests for structure tools - modules, pages, files."""

from __future__ import annotations

import pytest

from canvas_cli.models import AuthContext
from canvas_cli.tools.structure import (
    canvas_list_modules,
    canvas_list_module_items,
    canvas_list_pages,
    canvas_list_files,
    serialize_module,
    serialize_module_item,
    serialize_page,
    serialize_file,
)


@pytest.mark.integration
class TestCanvasListModules:
    """Integration tests for canvas_list_modules tool."""

    def test_list_modules_success(self, auth_context, sample_course_id):
        """Test listing modules with valid auth."""
        result = canvas_list_modules(auth_context, course_id=sample_course_id)

        assert result["ok"] is True
        assert result["tool"] == "canvas_list_modules"
        assert "items" in result

    def test_list_modules_pagination(self, auth_context, sample_course_id):
        """Test listing modules with pagination."""
        result = canvas_list_modules(
            auth_context,
            course_id=sample_course_id,
            page=1,
            page_size=10,
        )

        assert result["ok"] is True
        assert result["pagination"]["page"] == 1

    def test_module_has_expected_fields(self, auth_context, sample_course_id):
        """Test that module response has expected fields."""
        result = canvas_list_modules(auth_context, course_id=sample_course_id)

        if result["items"]:
            module = result["items"][0]
            expected_fields = [
                "id",
                "name",
                "course_id",
                "position",
                "state",
            ]

            for field in expected_fields:
                assert field in module, f"Missing field: {field}"


@pytest.mark.integration
class TestCanvasListModuleItems:
    """Integration tests for canvas_list_module_items tool."""

    def test_list_module_items_success(self, auth_context, sample_course_id):
        """Test listing module items."""
        # First get a module
        modules_result = canvas_list_modules(auth_context, course_id=sample_course_id)

        if not modules_result["items"]:
            pytest.skip("No modules available for testing")

        module_id = modules_result["items"][0]["id"]

        result = canvas_list_module_items(
            auth_context,
            course_id=sample_course_id,
            module_id=module_id,
        )

        assert result["ok"] is True
        assert result["tool"] == "canvas_list_module_items"
        assert "items" in result


@pytest.mark.integration
class TestCanvasListPages:
    """Integration tests for canvas_list_pages tool."""

    def test_list_pages_success(self, auth_context, sample_course_id):
        """Test listing pages with valid auth."""
        result = canvas_list_pages(auth_context, course_id=sample_course_id)

        assert result["ok"] is True
        assert result["tool"] == "canvas_list_pages"
        assert "items" in result

    def test_list_pages_pagination(self, auth_context, sample_course_id):
        """Test listing pages with pagination."""
        result = canvas_list_pages(
            auth_context,
            course_id=sample_course_id,
            page=1,
            page_size=10,
        )

        assert result["ok"] is True


@pytest.mark.integration
class TestCanvasListFiles:
    """Integration tests for canvas_list_files tool."""

    def test_list_files_success(self, auth_context, sample_course_id):
        """Test listing files with valid auth."""
        result = canvas_list_files(auth_context, course_id=sample_course_id)

        assert result["ok"] is True
        assert result["tool"] == "canvas_list_files"
        assert "items" in result

    def test_file_has_expected_fields(self, auth_context, sample_course_id):
        """Test that file response has expected fields."""
        result = canvas_list_files(auth_context, course_id=sample_course_id)

        if result["items"]:
            file = result["items"][0]
            expected_fields = [
                "id",
                "filename",
                "display_name",
                "content_type",
                "size",
            ]

            for field in expected_fields:
                assert field in file, f"Missing field: {field}"


@pytest.mark.integration
class TestStructureToolErrors:
    """Tests for structure tool error handling."""

    def test_list_modules_invalid_course(self, auth_context):
        """Test listing modules with invalid course ID."""
        result = canvas_list_modules(auth_context, course_id=999999999)

        assert result["ok"] is False
        assert len(result["errors"]) > 0

    def test_list_pages_invalid_course(self, auth_context):
        """Test listing pages with invalid course ID."""
        result = canvas_list_pages(auth_context, course_id=999999999)

        assert result["ok"] is False


class TestSerializeModule:
    """Unit tests for serialize_module function."""

    def test_serialize_module_basic(self):
        """Test serializing basic module."""
        class MockModule:
            id = 123
            name = "Module 1"
            course_id = 456
            position = 1
            state = "active"
            published = True
            items_count = 5
            items_url = "https://example.com/items"

        result = serialize_module(MockModule())

        assert result["id"] == 123
        assert result["name"] == "Module 1"
        assert result["position"] == 1
        assert result["state"] == "active"


class TestSerializeModuleItem:
    """Unit tests for serialize_module_item function."""

    def test_serialize_module_item_basic(self):
        """Test serializing basic module item."""
        class MockItem:
            id = 123
            module_id = 456
            title = "Assignment 1"
            type = "Assignment"
            position = 1
            html_url = "https://example.com/assignment"
            published = True

        result = serialize_module_item(MockItem())

        assert result["id"] == 123
        assert result["title"] == "Assignment 1"
        assert result["type"] == "Assignment"


class TestSerializePage:
    """Unit tests for serialize_page function."""

    def test_serialize_page_basic(self):
        """Test serializing basic page."""
        class MockPage:
            page_id = 123
            url = "page-slug"
            title = "Page Title"
            body = "<p>Content</p>"
            course_id = 456
            front_page = False
            published = True
            html_url = "https://example.com/page"

        result = serialize_page(MockPage())

        assert result["id"] == 123
        assert result["title"] == "Page Title"
        assert result["url"] == "page-slug"


class TestSerializeFile:
    """Unit tests for serialize_file function."""

    def test_serialize_file_basic(self):
        """Test serializing basic file."""
        class MockFile:
            id = 123
            uuid = "abc-123-def"
            display_name = "document.pdf"
            filename = "document.pdf"
            folder_id = 456
            content_type = "application/pdf"
            size = 1024
            url = "https://example.com/files/123/download"
            html_url = "https://example.com/files/123"
            locked = False

        result = serialize_file(MockFile())

        assert result["id"] == 123
        assert result["display_name"] == "document.pdf"
        assert result["content_type"] == "application/pdf"
        assert result["size"] == 1024
