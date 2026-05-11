"""
test_pipeline.py
Runs the full multi-agent blog generation pipeline directly (no HTTP server needed).
Tests with the exact assignment topic.

Run from phase3_agent/backend/:
    python test_pipeline.py
"""

from dotenv import load_dotenv
load_dotenv()

from agent import BlogRunner

TOPIC = "When to Use an AI-Agent"

def main():
    print("=" * 60)
    print(f"TOPIC: {TOPIC}")
    print("=" * 60)

    print("\n[1/1] Running pipeline...")
    runner = BlogRunner()
    result = runner.run(TOPIC)

    print(f"\n{'=' * 60}")
    print(f"SUPERVISOR RETRIES: {result.retry_count}")
    print(f"{'=' * 60}")

    print(f"\n--- RESEARCH NOTES ---\n{result.research_notes[:500]}...")

    print(f"\n--- OUTLINE ---\n{result.outline[:500]}...")

    print(f"\n--- SUPERVISOR FEEDBACK ---\n{result.supervisor_feedback or '(none — approved first pass)'}")

    print(f"\n--- FINAL BLOG POST ---\n{result.blog_post}")

    print(f"\n{'=' * 60}")
    print("Pipeline complete.")

if __name__ == "__main__":
    main()
