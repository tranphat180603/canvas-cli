"""
Test canvas_get_delta_bundle tool with different since dates.
"""
import os
import time
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("CANVAS_API_URL")
API_KEY = os.getenv("CANVAS_API_KEY")

COURSE_ID = 50000001397881  # MC 2025 FALL-CSC110AB 23092


def test_bundle(auth, since: str | None, label: str):
    """Test canvas_get_delta_bundle with a specific since date."""
    from canvas_cli.tools.bundle import canvas_get_delta_bundle

    print("=" * 60)
    print(f"📦 TEST canvas_get_delta_bundle - {label}")
    print("=" * 60)
    print(f"Since: {since}")

    start = time.time()

    result = canvas_get_delta_bundle(
        auth,
        course_ids=[COURSE_ID],
        since=since,
    )

    elapsed = time.time() - start

    print(f"\nok: {result['ok']}")
    print(f"⏱️  Time: {elapsed:.2f}s")

    if result.get('errors'):
        print(f"Errors: {result['errors']}")

    if result.get('items'):
        bundle = result['items'][0]

        print(f"\n--- Bundle Contents ---")
        print(f"Profile: {'✓' if bundle.get('profile') else '✗'}")
        print(f"Courses: {len(bundle.get('courses', []))}")
        print(f"Todo items: {len(bundle.get('todo_items', []))}")
        print(f"Upcoming events: {len(bundle.get('upcoming_events', []))}")
        print(f"Calendar events: {len(bundle.get('calendar_events', []))}")
        print(f"Planner items: {len(bundle.get('planner_items', []))}")

        if str(COURSE_ID) in bundle.get('course_data', {}):
            cd = bundle['course_data'][str(COURSE_ID)]
            print(f"\n--- Course Data for {COURSE_ID} ---")
            print(f"Assignments: {len(cd.get('assignments', []))}")
            print(f"Quizzes: {len(cd.get('quizzes', []))}")
            print(f"Discussions: {len(cd.get('discussions', []))}")
            print(f"Announcements: {len(cd.get('announcements', []))}")

            # Print all quizzes with details
            if cd.get('quizzes'):
                print(f"\n--- Quiz Details ---")
                for q in cd['quizzes']:
                    title = q.get('title', '?')[:50]
                    quiz_id = q.get('id', '?')
                    due = q.get('due_at', 'no due')
                    if due and len(due) > 10:
                        due = due[:10]
                    points = q.get('points_possible', '?')
                    published = q.get('published', '?')
                    print(f"  [{quiz_id}] {title}")
                    print(f"      Due: {due} | Points: {points} | Published: {published}")

    print("\n" + "=" * 60)
    return result


def main():
    from canvas_cli.models import AuthContext

    auth = AuthContext(canvas_base_url=API_URL, canvas_access_token=API_KEY)

    # Test 1: Since today (2026-02-23)
    print("\n" + "🔵" * 30)
    print("TEST 1: Since TODAY (2026-02-23)")
    print("🔵" * 30 + "\n")
    test_bundle(auth, since="2026-02-23T00:00:00Z", label="Since Today")

    print("\n\n")

    # Test 2: Since 2025-12-12
    print("\n" + "🟢" * 30)
    print("TEST 2: Since 2025-12-12")
    print("🟢" * 30 + "\n")
    test_bundle(auth, since="2025-12-12T00:00:00Z", label="Since Dec 12, 2025")


if __name__ == "__main__":
    main()
