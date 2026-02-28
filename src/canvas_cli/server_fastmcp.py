"""FastMCP Server for Canvas CLI - Modern MCP server implementation."""

from __future__ import annotations

import json
import logging
import os

from dotenv import load_dotenv
from fastmcp import FastMCP

from .tools import (
    canvas_get_conversation,
    canvas_get_delta_bundle,
    canvas_get_discussion_entries,
    canvas_get_discussion_replies,
    canvas_get_profile,
    canvas_get_todo_items,
    canvas_get_upcoming_events,
    canvas_get_calendar_events,
    canvas_get_planner_items,
    canvas_list_announcements,
    canvas_list_assignment_groups,
    canvas_list_assignments,
    canvas_list_conversations,
    canvas_list_courses,
    canvas_list_discussion_topics,
    canvas_list_files,
    canvas_list_module_items,
    canvas_list_modules,
    canvas_list_pages,
    canvas_list_quizzes,
)

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

    Authentication: Pass auth in tool calls with canvas_base_url and canvas_access_token,
    or set CANVAS_API_URL and CANVAS_API_KEY environment variables.
    """,
)

# Register all tools directly
# Each tool function handles auth resolution internally
mcp.tool(canvas_get_profile)
mcp.tool(canvas_list_courses)
mcp.tool(canvas_get_todo_items)
mcp.tool(canvas_get_upcoming_events)
mcp.tool(canvas_get_calendar_events)
mcp.tool(canvas_get_planner_items)
mcp.tool(canvas_list_assignments)
mcp.tool(canvas_list_quizzes)
mcp.tool(canvas_list_assignment_groups)
mcp.tool(canvas_list_discussion_topics)
mcp.tool(canvas_get_discussion_entries)
mcp.tool(canvas_get_discussion_replies)
mcp.tool(canvas_list_conversations)
mcp.tool(canvas_get_conversation)
mcp.tool(canvas_list_announcements)
mcp.tool(canvas_list_modules)
mcp.tool(canvas_list_module_items)
mcp.tool(canvas_list_pages)
mcp.tool(canvas_list_files)
mcp.tool(canvas_get_delta_bundle)


def run():
    """Run the FastMCP server."""
    logger.info("Starting Canvas CLI FastMCP server with 20 tools")

    # Check for environment credentials
    canvas_url = os.getenv("CANVAS_API_URL")
    canvas_token = os.getenv("CANVAS_API_KEY")
    if canvas_url and canvas_token:
        logger.info("Found Canvas credentials in environment")
    else:
        logger.info("No server-wide credentials - clients must pass auth in tool calls")

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    if os.getenv("PORT"):
        logger.info(f"Running streamable-http on {host}:{port}")
        mcp.run(transport="streamable-http", host=host, port=port)
    else:
        logger.info("Running stdio for local development")
        mcp.run()


if __name__ == "__main__":
    run()
