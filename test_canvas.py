"""
Fetch announcements and discussions from Canvas.
"""
import os
import re
from dotenv import load_dotenv
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

load_dotenv()

API_URL = os.getenv("CANVAS_API_URL")
API_KEY = os.getenv("CANVAS_API_KEY")


def strip_html(text, max_len=500):
    """Remove HTML tags and truncate."""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) > max_len:
        return clean[:max_len] + "..."
    return clean


def main():
    canvas = Canvas(API_URL, API_KEY)
    user = canvas.get_current_user()
    courses = list(user.get_courses())
    course = courses[0]

    print("=" * 70)
    print(f"ANNOUNCEMENTS & DISCUSSIONS: {course.name}")
    print("=" * 70)

    # ============================================
    # ANNOUNCEMENTS
    # ============================================
    print("\n" + "─" * 70)
    print("📢 ANNOUNCEMENTS")
    print("─" * 70)

    try:
        # Get announcements (discussion topics with only_announcements=True)
        announcements = list(course.get_discussion_topics(only_announcements=True))
        print(f"\nFound {len(announcements)} announcements\n")

        for i, ann in enumerate(announcements, 1):
            print(f"\n[{i}] {ann.title}")
            print(f"    Posted: {ann.posted_at}")
            author = ann.author.get('display_name', 'Unknown') if isinstance(ann.author, dict) else 'Unknown'
            print(f"    Author: {author}")
            print(f"    URL: {ann.html_url if hasattr(ann, 'html_url') else 'N/A'}")
            print(f"\n    {strip_html(ann.message, 400)}")

            # Get replies if any
            if hasattr(ann, 'discussion_subentry_count') and ann.discussion_subentry_count > 0:
                print(f"\n    💬 {ann.discussion_subentry_count} replies")

    except CanvasException as e:
        print(f"Error fetching announcements: {e}")

    # ============================================
    # DISCUSSIONS
    # ============================================
    print("\n" + "=" * 70)
    print("💬 DISCUSSION TOPICS")
    print("=" * 70)

    try:
        # Get all discussion topics (not just announcements)
        discussions = list(course.get_discussion_topics())
        # Filter out announcements
        regular_discussions = [d for d in discussions if not d.is_announcement]

        print(f"\nFound {len(regular_discussions)} discussion topics\n")

        for i, disc in enumerate(regular_discussions, 1):
            print(f"\n[{i}] {disc.title}")
            print(f"    Created: {disc.created_at}")
            author = disc.author.get('display_name', 'Unknown') if isinstance(disc.author, dict) else 'Unknown'
            print(f"    Author: {author}")
            print(f"    Replies: {disc.discussion_subentry_count if hasattr(disc, 'discussion_subentry_count') else 0}")
            print(f"    URL: {disc.html_url if hasattr(disc, 'html_url') else 'N/A'}")
            print(f"\n    {strip_html(disc.message, 300)}")

            # Try to get discussion entries (replies)
            try:
                entries = list(disc.get_topic_entries())
                if entries:
                    print(f"\n    📝 Recent replies:")
                    for entry in entries[:3]:  # Show first 3 replies
                        author = entry.user_name if hasattr(entry, 'user_name') else 'Unknown'
                        print(f"       - {author}: {strip_html(entry.message, 100)}")
                    if len(entries) > 3:
                        print(f"       ... and {len(entries) - 3} more replies")
            except:
                pass

    except CanvasException as e:
        print(f"Error fetching discussions: {e}")

    # ============================================
    # RECENT ACTIVITY
    # ============================================
    print("\n" + "=" * 70)
    print("📋 SUMMARY")
    print("=" * 70)
    print(f"\n  Course: {course.name}")
    print(f"  Total Announcements: {len(announcements) if 'announcements' in dir() else 0}")
    print(f"  Total Discussions: {len(regular_discussions) if 'regular_discussions' in dir() else 0}")


if __name__ == "__main__":
    main()
