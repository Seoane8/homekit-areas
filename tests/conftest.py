"""Pytest fixtures for HomeKit Areas tests.

The ``pytest_homeassistant_custom_component`` plugin provides the ``hass``
fixture and Home Assistant's testing helpers. The
``enable_custom_integrations`` fixture makes the ``custom_components`` package
loadable inside the test Home Assistant instance.
"""

import pytest

pytest_plugins = ("pytest_homeassistant_custom_component",)


@pytest.fixture(autouse=True)
def _enable_custom_integrations(enable_custom_integrations):
    """Enable loading of custom components in tests."""
    yield
