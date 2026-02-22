"""
Test canvas_list_quizzes tool (with module fallback).
"""
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("CANVAS_API_URL")
API_KEY = os.getenv("CANVAS_API_KEY")

COURSE_ID = 50000001397881  # MC 2025 FALL-CSC110AB 23092


def main():
    from canvas_cli.models import AuthContext
    from canvas_cli.tools.assignments import canvas_list_quizzes

    auth = AuthContext(canvas_base_url=API_URL, canvas_access_token=API_KEY)

    print("=" * 50)
    print("📝 TEST canvas_list_quizzes")
    print("=" * 50)

    result = canvas_list_quizzes(auth, course_id=COURSE_ID)

    print(f"\nok: {result['ok']}")
    print(f"Total quizzes: {len(result['items'])}")
    if result.get('errors'):
        print(f"Info: {result['errors']}")

    if result['items']:
        print(f"\nQuizzes found:")
        for q in result['items'][:15]:
            title = q.get('title', '?')[:45]
            quiz_id = q.get('id', '?')
            print(f"  - [{quiz_id}] {title}")

        if len(result['items']) > 15:
            print(f"\n... and {len(result['items']) - 15} more")

    print("\n" + "=" * 50)
    if result['ok'] and result['items']:
        print("✅ TOOL WORKS!")
    else:
        print("❌ TOOL FAILED")
    print("=" * 50)


if __name__ == "__main__":
    main()
