"""
Test the stateless focus group API flow
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from focus_group.engine import FocusGroupEngine


def main():
    print("=" * 60)
    print("STATELESS FOCUS GROUP TEST")
    print("=" * 60)

    engine = FocusGroupEngine()

    # Question 1 - no history
    print("\n1. First question (no history)")
    print("   Q: What comes to mind when you think of premium chocolate?")
    print("-" * 60)

    result1 = engine.ask_stateless(
        question="What comes to mind when you think of premium chocolate?",
        audience_id="premium_chocolate",
        history=None
    )

    for r in result1["responses"]:
        print(f"\n{r['persona_name'].upper()}:")
        print(f"   {r['text'][:200]}...")

    history = result1["history"]
    print(f"\n   [History now has {len(history)} messages]")

    # Question 2 - with history
    print("\n" + "=" * 60)
    print("2. Follow-up question (with history)")
    print("   Q: How does that compare to grocery store chocolate?")
    print("-" * 60)

    result2 = engine.ask_stateless(
        question="How does that compare to grocery store chocolate?",
        audience_id="premium_chocolate",
        history=history
    )

    for r in result2["responses"]:
        print(f"\n{r['persona_name'].upper()}:")
        print(f"   {r['text'][:200]}...")

    history = result2["history"]
    print(f"\n   [History now has {len(history)} messages]")

    # Question 3 - 1:1 with specific persona
    print("\n" + "=" * 60)
    print("3. Direct question to Marcus (1:1 mode)")
    print("   Q: Marcus, tell me more about your girlfriend's influence")
    print("-" * 60)

    result3 = engine.ask_persona_stateless(
        persona_id=1,
        question="Tell me more about your girlfriend's influence on your chocolate preferences",
        audience_id="premium_chocolate",
        history=history
    )

    print(f"\n{result3['response']['persona_name'].upper()}:")
    print(f"   {result3['response']['text']}")

    history = result3["history"]
    print(f"\n   [History now has {len(history)} messages]")

    # Show final transcript
    print("\n" + "=" * 60)
    print("FINAL TRANSCRIPT")
    print("=" * 60)
    for msg in history:
        role = msg["role"]
        if role == "moderator":
            print(f"\nMODERATOR: {msg['text']}")
        else:
            print(f"\n{msg['persona_name'].upper()}: {msg['text'][:150]}...")


if __name__ == "__main__":
    main()
