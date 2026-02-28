"""Structure tools - modules, pages, files."""

from typing import Any, Dict, List, Optional

from canvasapi.exceptions import CanvasException

from ..canvas_client import CanvasClient
from ..utils.normalize_time import normalize_canvas_time
from ..utils.pagination import build_tool_output
from .auth import resolve_auth


def serialize_module(module: Any) -> Dict[str, Any]:
    """Serialize a Canvas Module to dict."""
    return {
        "id": getattr(module, "id", None),
        "name": getattr(module, "name", None),
        "course_id": getattr(module, "course_id", None),
        "position": getattr(module, "position", None),
        "unlock_at": normalize_canvas_time(getattr(module, "unlock_at", None)),
        "require_sequential_progress": getattr(module, "require_sequential_progress", False),
        "publish_final_grade": getattr(module, "publish_final_grade", False),
        "published": getattr(module, "published", None),
        "items_count": getattr(module, "items_count", None),
        "items_url": getattr(module, "items_url", None),
        "state": getattr(module, "state", None),
        "completed_at": normalize_canvas_time(getattr(module, "completed_at", None)),
        "created_at": normalize_canvas_time(getattr(module, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(module, "updated_at", None)),
    }


def serialize_module_item(item: Any) -> Dict[str, Any]:
    """Serialize a Canvas Module Item to dict."""
    return {
        "id": getattr(item, "id", None),
        "module_id": getattr(item, "module_id", None),
        "position": getattr(item, "position", None),
        "title": getattr(item, "title", None),
        "type": getattr(item, "type", None),
        "content_id": getattr(item, "content_id", None),
        "content_type": getattr(item, "content_type", None),
        "html_url": getattr(item, "html_url", None),
        "url": getattr(item, "url", None),
        "external_url": getattr(item, "external_url", None),
        "page_url": getattr(item, "page_url", None),
        "indent": getattr(item, "indent", None),
        "completion_requirement": getattr(item, "completion_requirement", None),
        "published": getattr(item, "published", None),
        "new_tab": getattr(item, "new_tab", False),
        "created_at": normalize_canvas_time(getattr(item, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(item, "updated_at", None)),
    }


def serialize_page(page: Any) -> Dict[str, Any]:
    """Serialize a Canvas Page to dict."""
    return {
        "id": getattr(page, "page_id", None) or getattr(page, "id", None),
        "url": getattr(page, "url", None),
        "title": getattr(page, "title", None),
        "body": getattr(page, "body", None),
        "course_id": getattr(page, "course_id", None),
        "front_page": getattr(page, "front_page", False),
        "published": getattr(page, "published", None),
        "hide_from_students": getattr(page, "hide_from_students", False),
        "editing_roles": getattr(page, "editing_roles", None),
        "last_edited_by": getattr(page, "last_edited_by", None),
        "html_url": getattr(page, "html_url", None),
        "todo_date": normalize_canvas_time(getattr(page, "todo_date", None)),
        "created_at": normalize_canvas_time(getattr(page, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(page, "updated_at", None)),
    }


def serialize_file(file: Any) -> Dict[str, Any]:
    """Serialize a Canvas File to dict."""
    return {
        "id": getattr(file, "id", None),
        "uuid": getattr(file, "uuid", None),
        "display_name": getattr(file, "display_name", None),
        "filename": getattr(file, "filename", None),
        "folder_id": getattr(file, "folder_id", None),
        "content_type": getattr(file, "content_type", None),
        "size": getattr(file, "size", None),
        "url": getattr(file, "url", None),
        "html_url": getattr(file, "html_url", None),
        "thumbnail_url": getattr(file, "thumbnail_url", None),
        "locked": getattr(file, "locked", False),
        "locked_for_user": getattr(file, "locked_for_user", False),
        "hidden": getattr(file, "hidden", False),
        "hidden_for_user": getattr(file, "hidden_for_user", False),
        "upload_status": getattr(file, "upload_status", None),
        "created_at": normalize_canvas_time(getattr(file, "created_at", None)),
        "updated_at": normalize_canvas_time(getattr(file, "updated_at", None)),
        "modified_at": normalize_canvas_time(getattr(file, "modified_at", None)),
    }


def canvas_list_modules(
    auth: Optional[Dict[str, Any]] = None,
    *,
    course_id: int,
    page: int = 1,
    page_size: int = 100,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List modules for a course.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        course_id: Canvas course ID
        page: Page number
        page_size: Items per page
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with modules
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)
        course = client.get_course(course_id)

        paginated = course.get_modules()
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        # Filter by since if provided
        if since:
            from ..utils.normalize_time import is_after

            items = [
                item
                for item in items
                if is_after(getattr(item, "updated_at", None), since)
            ]

        modules = [serialize_module(module) for module in items]

        return build_tool_output(
            tool="canvas_list_modules",
            items=modules,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_list_modules",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_list_modules",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )


def canvas_list_module_items(
    auth: Optional[Dict[str, Any]] = None,
    *,
    course_id: int,
    module_id: int,
    page: int = 1,
    page_size: int = 100,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List items in a module.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        course_id: Canvas course ID
        module_id: Canvas module ID
        page: Page number
        page_size: Items per page
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with module items
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)
        course = client.get_course(course_id)

        module = course.get_module(module_id)
        paginated = module.get_module_items()
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        # Filter by since if provided
        if since:
            from ..utils.normalize_time import is_after

            items = [
                item
                for item in items
                if is_after(getattr(item, "updated_at", None), since)
            ]

        module_items = [serialize_module_item(item) for item in items]

        return build_tool_output(
            tool="canvas_list_module_items",
            items=module_items,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_list_module_items",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_list_module_items",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )


def canvas_list_pages(
    auth: Optional[Dict[str, Any]] = None,
    *,
    course_id: int,
    page: int = 1,
    page_size: int = 100,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List pages for a course.

    Note: Some Canvas instances don't allow direct page listing.
    This tool will try the direct API first, then fall back to
    extracting pages from modules.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        course_id: Canvas course ID
        page: Page number
        page_size: Items per page
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with pages
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)
        course = client.get_course(course_id)

        all_pages = []

        # Try direct API first
        try:
            paginated = course.get_pages()
            items, _ = CanvasClient.extract_paginated_list(paginated, 1, 1000)
            all_pages = [serialize_page(p) for p in items]
        except Exception:
            # Direct API failed, use fallback
            errors.append("Direct pages API unavailable, using module fallback")

        # Fallback: Extract pages from modules if direct API failed
        if not all_pages:
            modules = list(course.get_modules())

            for module in modules:
                try:
                    module_items = list(module.get_module_items())
                    for item in module_items:
                        if getattr(item, 'type', None) == 'Page':
                            page_url = getattr(item, 'page_url', None)
                            if page_url:
                                try:
                                    p = course.get_page(page_url)
                                    all_pages.append(serialize_page(p))
                                except Exception:
                                    all_pages.append({
                                        "url": page_url,
                                        "title": getattr(item, 'title', None),
                                        "course_id": course_id,
                                    })
                except Exception:
                    continue

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_pages = all_pages[start_idx:end_idx]
        has_more = len(all_pages) > end_idx

        return build_tool_output(
            tool="canvas_list_pages",
            items=paginated_pages,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_list_pages",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_list_pages",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )


def canvas_list_files(
    auth: Optional[Dict[str, Any]] = None,
    *,
    course_id: int,
    page: int = 1,
    page_size: int = 100,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List files for a course.

    Args:
        auth: Canvas auth with canvas_base_url and canvas_access_token
        course_id: Canvas course ID
        page: Page number
        page_size: Items per page
        since: ISO timestamp for delta fetch

    Returns:
        Tool output with files
    """
    errors: List[str] = []

    try:
        auth_ctx = resolve_auth(auth)
        client = CanvasClient(auth_ctx)
        course = client.get_course(course_id)

        paginated = course.get_files()
        items, has_more = CanvasClient.extract_paginated_list(paginated, page, page_size)

        # Filter by since if provided
        if since:
            from ..utils.normalize_time import is_after

            items = [
                item
                for item in items
                if is_after(getattr(item, "updated_at", None), since)
            ]

        files = [serialize_file(f) for f in items]

        return build_tool_output(
            tool="canvas_list_files",
            items=files,
            page=page,
            page_size=page_size,
            has_more=has_more,
            errors=errors,
        )

    except CanvasException as e:
        errors.append(f"Canvas API error: {e}")
        return build_tool_output(
            tool="canvas_list_files",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return build_tool_output(
            tool="canvas_list_files",
            items=[],
            page=page,
            page_size=page_size,
            has_more=False,
            errors=errors,
        )
