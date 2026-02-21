"""Pytest configuration and fixtures for Canvas CLI tests."""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

# Load environment variables before importing anything else
load_dotenv()


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test requiring real API")


def get_canvas_credentials():
    """Get Canvas credentials from environment."""
    url = os.getenv("CANVAS_API_URL")
    key = os.getenv("CANVAS_API_KEY")
    return url, key


def skip_if_no_credentials():
    """Skip tests if Canvas credentials are not available."""
    url, key = get_canvas_credentials()
    if not url or not key:
        pytest.skip("CANVAS_API_URL and CANVAS_API_KEY environment variables required")


@pytest.fixture
def canvas_credentials():
    """Fixture providing Canvas credentials."""
    skip_if_no_credentials()
    return get_canvas_credentials()


@pytest.fixture
def auth_context():
    """Fixture providing AuthContext for Canvas API."""
    skip_if_no_credentials()
    from canvas_cli.models import AuthContext

    url, key = get_canvas_credentials()
    return AuthContext(canvas_base_url=url, canvas_access_token=key)


@pytest.fixture
def sample_course_id(auth_context):
    """Fixture providing a valid course ID for testing."""
    from canvas_cli.canvas_client import CanvasClient

    client = CanvasClient(auth_context)
    user = client.get_current_user()
    courses = list(user.get_courses(enrollment_state=["active"]))

    if not courses:
        pytest.skip("No active courses found for testing")

    return courses[0].id
