"""MCP Server entry point for Canvas CLI."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .models import AuthContext
from .tools import TOOL_REGISTRY

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("canvas-cli")

# Create MCP server
server = Server("canvas-cli")


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


def serialize_result(result: Any) -> str:
    """Serialize a result to JSON string."""
    if isinstance(result, dict):
        return json.dumps(result, default=str)
    return str(result)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Canvas tools."""
    tools = []
    for name, config in TOOL_REGISTRY.items():
        tool = Tool(
            name=name,
            description=config["description"],
            inputSchema=config["parameters"],
        )
        tools.append(tool)
    logger.info(f"Listed {len(tools)} tools")
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Call a Canvas tool with the given arguments."""
    logger.info(f"Calling tool: {name}")

    if name not in TOOL_REGISTRY:
        error_msg = f"Unknown tool: {name}. Available tools: {list(TOOL_REGISTRY.keys())}"
        logger.error(error_msg)
        return [TextContent(type="text", text=json.dumps({"error": error_msg}))]

    tool_config = TOOL_REGISTRY[name]
    tool_func = tool_config["function"]

    # Get auth - first try from args, then from env
    auth = get_auth_from_args(arguments)
    if auth is None:
        auth = get_auth_from_env()

    if auth is None:
        error_msg = "No authentication provided. Set CANVAS_API_URL and CANVAS_API_KEY environment variables, or pass auth in arguments."
        logger.error(error_msg)
        return [TextContent(type="text", text=json.dumps({"error": error_msg, "ok": False}))]

    # Update arguments with resolved auth
    args = {**arguments, "auth": auth}

    try:
        # Call the tool function
        # Tool functions are synchronous, so we call them directly
        result = tool_func(**args)

        logger.info(f"Tool {name} completed successfully")
        return [TextContent(type="text", text=serialize_result(result))]

    except Exception as e:
        error_msg = f"Error calling tool {name}: {str(e)}"
        logger.exception(error_msg)
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "ok": False,
                        "tool": name,
                        "source": "canvas",
                        "errors": [error_msg],
                        "items": [],
                    }
                ),
            )
        ]


async def run_server():
    """Run the MCP server."""
    logger.info("Starting Canvas CLI MCP server")

    # Check for auth
    auth = get_auth_from_env()
    if auth:
        logger.info("Found Canvas credentials in environment")
    else:
        logger.warning(
            "No Canvas credentials found in environment. "
            "Set CANVAS_API_URL and CANVAS_API_KEY, or pass auth in tool calls."
        )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    """Main entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
