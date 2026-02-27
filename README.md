# Canvas CLI - FastMCP Server

A FastMCP server that exposes Canvas LMS data as tools for AI agent workflows.

## Features

- **20 MCP Tools** for comprehensive Canvas data access
- **Multi-tenant** - clients send their own Canvas credentials
- **FastMCP 3.0** - modern, production-ready MCP framework
- **HTTP transport** - deploy anywhere (Railway, Docker, etc.)
- **Pagination** support for all list endpoints
- **Delta sync** with `since` timestamp parameter

## Available Tools

| Tool | Description |
|------|-------------|
| `canvas_get_profile` | Get the current user's Canvas profile |
| `canvas_list_courses` | List courses for the current user |
| `canvas_get_todo_items` | Get todo items |
| `canvas_get_upcoming_events` | Get upcoming events |
| `canvas_get_calendar_events` | Get calendar events |
| `canvas_get_planner_items` | Get planner items |
| `canvas_list_assignments` | List assignments (with optional submissions) |
| `canvas_list_quizzes` | List quizzes for a course |
| `canvas_list_assignment_groups` | List assignment groups with weights |
| `canvas_list_discussion_topics` | List discussion topics |
| `canvas_get_discussion_entries` | Get entries for a discussion |
| `canvas_get_discussion_replies` | Get replies for an entry |
| `canvas_list_conversations` | List inbox conversations |
| `canvas_get_conversation` | Get a single conversation |
| `canvas_list_announcements` | List course announcements |
| `canvas_list_modules` | List course modules |
| `canvas_list_module_items` | List items in a module |
| `canvas_list_pages` | List course pages |
| `canvas_list_files` | List course files |
| `canvas_get_delta_bundle` | Aggregate bundle of multiple data sources |

## Authentication

This server is **multi-tenant** - each client sends their own Canvas credentials with every tool call.

### Tool Call with Auth

```json
{
  "auth": {
    "canvas_base_url": "https://your-school.instructure.com/api/v1",
    "canvas_access_token": "your_canvas_token"
  },
  "course_id": 12345
}
```

### Getting a Canvas Access Token

1. Log in to your Canvas account
2. Go to **Account > Settings**
3. Scroll to **Approved Integrations**
4. Click **New Access Token**
5. Give it a purpose and expiration
6. Copy the token (you won't see it again!)

## Installation

### Local Development

```bash
# Clone and install
git clone <repository-url>
cd canvas-cli
pip install -e .

# Run locally (stdio transport for Claude Desktop)
python -m canvas_cli.server_fastmcp
```

### Docker

```bash
# Build
docker build -t canvas-cli .

# Run
docker run -p 8000:8000 canvas-cli
```

## Deployment

### Railway

1. **Connect your GitHub repository** to Railway

2. **Configure environment variables** (optional):
   - `PORT` - Railway sets this automatically

3. **Deploy** - Railway will detect the Dockerfile and build

4. **Your server URL** will be: `https://your-app.railway.app/mcp`

### Environment Variables
NOT REQUIRED. SEND BY CLIENT



### Connecting MCP Clients

Configure your MCP client to connect to the HTTP endpoint:

```json
{
  "mcpServers": {
    "canvas": {
      "url": "https://your-app.railway.app/mcp",
      "transport": "http"
    }
  }
}
```

## Tool Output Format

All tools return a consistent JSON structure:

```json
{
  "ok": true,
  "source": "canvas",
  "tool": "canvas_list_courses",
  "items": [...],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "next_page": 2
  },
  "fetched_at": "2024-01-15T10:30:00Z",
  "errors": []
}
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v
```

### Project Structure

```
canvas-cli/
├── src/canvas_cli/
│   ├── __init__.py
│   ├── server_fastmcp.py   # FastMCP server entry point
│   ├── models.py           # Pydantic models
│   ├── canvas_client.py    # Canvas API client
│   ├── tools/
│   │   ├── profile.py
│   │   ├── courses.py
│   │   ├── schedule.py
│   │   ├── assignments.py
│   │   ├── discussions.py
│   │   ├── conversations.py
│   │   ├── announcements.py
│   │   ├── structure.py
│   │   └── bundle.py
│   └── utils/
│       ├── pagination.py
│       └── normalize_time.py
├── tests/
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

## License

MIT
