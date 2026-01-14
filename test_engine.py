"""
Quick test of the focus group engine
"""

import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from focus_group.engine import FocusGroupEngine


def main():
    print("=" * 60)
    print("FOCUS GROUP ENGINE TEST")
    print("=" * 60)

    # Initialize engine
    engine = FocusGroupEngine()

    # Load the premium chocolate audience
    print("\n1. Loading audience: premium_chocolate")
    personas = engine.load_audience("premium_chocolate")
    print(f"   Loaded {len(personas)} personas:")
    for p in personas:
        print(f"   - {p.name} ({p.age}, {p.occupation})")

    # Ask first question
    print("\n2. Asking group question...")
    print("   Q: What comes to mind when you think of premium chocolate?")
    print("-" * 60)

    responses = engine.ask("What comes to mind when you think of premium chocolate?")

    for r in responses:
        print(f"\n{r.persona_name.upper()}:")
        print(f"   {r.text}")

    # Ask follow-up
    print("\n" + "=" * 60)
    print("3. Asking follow-up question...")
    print("   Q: How does that compare to regular grocery store chocolate?")
    print("-" * 60)

    responses = engine.ask("How does that compare to regular grocery store chocolate?")

    for r in responses:
        print(f"\n{r.persona_name.upper()}:")
        print(f"   {r.text}")

    # Ask specific persona
    print("\n" + "=" * 60)
    print("4. Asking Marcus directly (1:1)...")
    print("   Q: Marcus, you mentioned your girlfriend - tell me more about that")
    print("-" * 60)

    response = engine.ask_persona(1, "You mentioned your girlfriend introduced you to nicer brands. Tell me more about that experience.")
    print(f"\n{response.persona_name.upper()}:")
    print(f"   {response.text}")

    # Show transcript
    print("\n" + "=" * 60)
    print("5. FULL TRANSCRIPT")
    print("=" * 60)
    print(engine.get_transcript_text())


if __name__ == "__main__":
    main()
