# canvas-cli

A Python MCP server that exposes Canvas LMS data as tools for Tomo agent workflows.

## Features

- **19 MCP Tools** for comprehensive Canvas data access
- **Authentication** via Canvas API tokens
- **Pagination** support for all list endpoints
- **Delta sync** with `since` timestamp parameter
- **Error handling** with structured error responses

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd canvas-cli

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

## Configuration

Set the following environment variables:

```bash
export CANVAS_API_URL="https://your-canvas-instance.instructure.com/api/v1"
export CANVAS_API_KEY="your_canvas_access_token"
```

Or create a `.env` file:

```
CANVAS_API_URL=https://your-canvas-instance.instructure.com/api/v1
CANVAS_API_KEY=your_canvas_access_token
```

### Getting a Canvas Access Token

1. Log in to your Canvas account
2. Go to Account > Settings
3. Scroll to "Approved Integrations"
4. Click "New Access Token"
5. Give it a purpose and expiration
6. Copy the token (you won't see it again!)

## Usage

### Running the MCP Server

```bash
# Run directly
python -m canvas_cli.server

# Or using the installed script
canvas-cli
```

### Using with Claude Code / MCP Clients

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "canvas": {
      "command": "python",
      "args": ["-m", "canvas_cli.server"],
      "env": {
        "CANVAS_API_URL": "https://your-canvas-instance.instructure.com/api/v1",
        "CANVAS_API_KEY": "your_canvas_access_token"
      }
    }
  }
}
```

## Available Tools

### Identity & Roster

| Tool | Description |
|------|-------------|
| `canvas_get_profile` | Get the current user's Canvas profile |
| `canvas_list_courses` | List courses for the current user |

### Scheduling

| Tool | Description |
|------|-------------|
| `canvas_get_todo_items` | Get todo items for the current user |
| `canvas_get_upcoming_events` | Get upcoming events |
| `canvas_get_calendar_events` | Get calendar events |
| `canvas_get_planner_items` | Get planner items |

### Coursework

| Tool | Description |
|------|-------------|
| `canvas_list_assignments` | List assignments for a course |
| `canvas_list_quizzes` | List quizzes for a course |

### Discussions

| Tool | Description |
|------|-------------|
| `canvas_list_discussion_topics` | List discussion topics for a course |
| `canvas_get_discussion_entries` | Get entries for a discussion topic |
| `canvas_get_discussion_replies` | Get replies for a discussion entry |

### Conversations

| Tool | Description |
|------|-------------|
| `canvas_list_conversations` | List inbox conversations |
| `canvas_get_conversation` | Get a single conversation with messages |

### Announcements

| Tool | Description |
|------|-------------|
| `canvas_list_announcements` | List announcements for courses |

### Course Structure

| Tool | Description |
|------|-------------|
| `canvas_list_modules` | List modules for a course |
| `canvas_list_module_items` | List items in a module |
| `canvas_list_pages` | List pages for a course |
| `canvas_list_files` | List files for a course |

### Bundle

| Tool | Description |
|------|-------------|
| `canvas_get_delta_bundle` | Get a comprehensive bundle of Canvas data |

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
    "next_page": 2,
    "total_count": 500
  },
  "fetched_at": "2024-01-15T10:30:00Z",
  "errors": []
}
```

## Authentication in Tool Calls

You can pass authentication directly in tool calls:

```json
{
  "auth": {
    "canvas_base_url": "https://canvas.example.com/api/v1",
    "canvas_access_token": "your_token"
  },
  "course_id": 12345
}
```

Or rely on environment variables for server-wide authentication.

## Development

### Running Tests

```bash
# Run all tests (requires Canvas credentials)
pytest tests/

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest tests/ -v
```

### Test Requirements

Integration tests require valid Canvas credentials:
- Set `CANVAS_API_URL` and `CANVAS_API_KEY` environment variables
- Tests will be skipped if credentials are not available

### Project Structure

```
canvas-cli/
├── src/canvas_cli/
│   ├── __init__.py
│   ├── server.py          # MCP server entry point
│   ├── auth.py            # Authentication handling
│   ├── models.py          # Pydantic models
│   ├── canvas_client.py   # Canvas API client wrapper
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
│       ├── retry.py
│       ├── normalize_time.py
│       └── ids.py
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_tools_*.py
│   └── test_pagination.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## License

MIT
