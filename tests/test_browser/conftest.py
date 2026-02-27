"""Conftest for browser integration tests.

Requires the ``test-browser`` extra:  uv pip install -e ".[test-browser]"
and Playwright browsers:             uv run playwright install chromium

When pytest-playwright is not installed a stub ``page`` fixture is registered
so pytest can collect the tests and issue a proper skip rather than an error.
"""

import pytest

try:
    import pytest_playwright as _pp  # noqa: F401
    _has_playwright = True
except ImportError:
    _has_playwright = False

if not _has_playwright:
    _SKIP_REASON = (
        "pytest-playwright not installed. "
        "Install with: uv pip install -e '.[test-browser]' && "
        "uv run playwright install chromium"
    )

    @pytest.fixture
    def page():  # type: ignore[empty-body]
        pytest.skip(_SKIP_REASON)
