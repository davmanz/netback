"""Package containing core app tests (renamed from core/tests).

This package is the canonical location for tests so that test discovery
of `manage.py test core` works without colliding with a top-level module
named `tests`.
"""

__all__ = [
    "test_autobackup_schedule",
    "test_endpoints_signals",
    "test_models_crud",
    "test_ping",
]
