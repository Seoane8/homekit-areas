"""HomeKit Areas.

A custom integration that manages one HomeKit Bridge (through the official
``homeassistant.components.homekit`` integration) per Home Assistant area.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the HomeKit Areas integration from YAML (not supported)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a HomeKit Areas config entry.

    The coordinator and bridge manager are wired in later phases. For the
    skeleton we only confirm the entry loads and can be reloaded.
    """
    _LOGGER.info("HomeKit Areas entry loaded: %s", entry.title)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a HomeKit Areas config entry.

    Later phases will stop the per-area bridges here.
    """
    return True
