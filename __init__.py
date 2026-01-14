"""
Focus Group Chat - IRM-based synthetic focus group API

Usage:
    from focus_group import FocusGroupEngine

    engine = FocusGroupEngine()
    engine.load_audience("premium_chocolate")
    responses = engine.ask("What comes to mind when you think of premium chocolate?")
"""

from .engine import FocusGroupEngine, Persona, Response

__all__ = ["FocusGroupEngine", "Persona", "Response"]
