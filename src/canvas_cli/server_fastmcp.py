"""FastMCP Server for Canvas CLI - Modern MCP server implementation."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP

from .models import AuthContext
from .tools import TOOL_REGISTRY

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("canvas-cli")

# Create FastMCP server
mcp = FastMCP(
    name="Canvas CLI",
    version="0.1.0",
    instructions="""
    Canvas CLI MCP Server - Access Canvas LMS data through MCP tools.

    This server provides tools to interact with Canvas LMS:
    - Profile: canvas_get_profile
    - Courses: canvas_list_courses
    - Assignments: canvas_list_assignments, canvas_list_quizzes, canvas_list_assignment_groups
    - Schedule: canvas_get_todo_items, canvas_get_upcoming_events, canvas_get_calendar_events, canvas_get_planner_items
    - Discussions: canvas_list_discussion_topics, canvas_get_discussion_entries, canvas_get_discussion_replies
    - Conversations: canvas_list_conversations, canvas_get_conversation
    - Announcements: canvas_list_announcements
    - Structure: canvas_list_modules, canvas_list_module_items, canvas_list_pages, canvas_list_files
    - Bundle: canvas_get_delta_bundle (aggregates multiple data sources)

    Authentication:
    Set CANVAS_API_URL and CANVAS_API_KEY environment variables, or pass auth in tool calls.
    """,
)


def get_auth_from_env() -> AuthContext | None:
    """Get authentication context from environment variables."""
    canvas_url = os.getenv("CANVAS_API_URL")
    canvas_token = os.getenv("CANVAS_API_KEY")

    if not canvas_url or not canvas_token:
        return None

    return AuthContext(canvas_base_url=canvas_url, canvas_access_token=canvas_token)


def get_auth_from_args(args: dict[str, Any]) -> AuthContext | None:
    """Get authentication context from tool arguments."""
    auth_data = args.get("auth", {})
    if not auth_data:
        return None

    canvas_url = auth_data.get("canvas_base_url") or auth_data.get("canvasApiUrl")
    canvas_token = auth_data.get("canvas_access_token") or auth_data.get("canvasApiKey")

    if not canvas_url or not canvas_token:
        return None

    return AuthContext(canvas_base_url=canvas_url, canvas_access_token=canvas_token)


def resolve_auth(**kwargs) -> AuthContext:
    """Resolve auth from kwargs or environment."""
    auth = get_auth_from_args(kwargs)
    if auth is None:
        auth = get_auth_from_env()
    if auth is None:
        raise ValueError(
            "No authentication provided. Set CANVAS_API_URL and CANVAS_API_KEY "
            "environment variables, or pass auth in arguments."
        )
    return auth


# Dynamically register all tools from TOOL_REGISTRY
for tool_name, tool_config in TOOL_REGISTRY.items():
    tool_func = tool_config["function"]
    tool_description = tool_config["description"]
    tool_params = tool_config["parameters"]

    # Get required parameters (excluding auth which we handle separately)
    required = tool_params.get("required", [])
    properties = tool_params.get("properties", {})

    # Build function signature dynamically
    # We wrap the original function to handle auth resolution
    def make_wrapper(original_func, name):
        def wrapper(**kwargs):
            try:
                # Resolve auth
                auth = resolve_auth(**kwargs)
                kwargs["auth"] = auth

                # Call original function
                result = original_func(**kwargs)

                # Return as JSON string for MCP
                if isinstance(result, dict):
                    return json.dumps(result, default=str)
                return str(result)
            except Exception as e:
                logger.exception(f"Error in tool {name}: {e}")
                return json.dumps({
                    "ok": False,
                    "tool": name,
                    "source": "canvas",
                    "errors": [str(e)],
                    "items": [],
                })

        return wrapper

    wrapped_func = make_wrapper(tool_func, tool_name)
    wrapped_func.__name__ = tool_name
    wrapped_func.__doc__ = tool_description

    # Register with FastMCP
    mcp.tool(wrapped_func)


def run():
    """Run the FastMCP server."""
    logger.info("Starting Canvas CLI FastMCP server")

    # Check for auth
    auth = get_auth_from_env()
    if auth:
        logger.info("Found Canvas credentials in environment")
    else:
        logger.warning(
            "No Canvas credentials found in environment. "
            "Set CANVAS_API_URL and CANVAS_API_KEY, or pass auth in tool calls."
        )

    # Run with HTTP transport for production (Railway)
    # Use environment variables for host/port configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    # Check if running in production (Railway sets PORT)
    if os.getenv("PORT"):
        logger.info(f"Running HTTP server on {host}:{port}")
        mcp.run(transport="http", host=host, port=port)
    else:
        # Default to stdio for local development (Claude Desktop)
        logger.info("Running stdio server for local development")
        mcp.run()


if __name__ == "__main__":
    run()
