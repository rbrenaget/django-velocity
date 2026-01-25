"""
Root-level pytest configuration.

Re-exports fixtures from tests/conftest.py so they are available
to all test files across the project (apps/*/tests/).
"""

from tests.conftest import *  # noqa: F401, F403
