"""Compatibility package to expose tests under `core.tests`.

Tests have been moved to `core.test_suite`. This module re-exports them so
`manage.py test core` can discover tests under the conventional
`core.tests` package name without duplicating files.
"""

from core.test_suite import (
    test_autobackup_schedule,
    test_endpoints_signals,
    test_models_crud,
    test_ping,
    test_helpers,
)

__all__ = [
    "test_autobackup_schedule",
    "test_endpoints_signals",
    "test_models_crud",
    "test_ping",
    "test_helpers",
]
# This package used to contain tests; tests were moved to `core.test_suite`.
# Leave this module present but empty to avoid import/discovery issues.

