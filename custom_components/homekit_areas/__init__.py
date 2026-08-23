"""HomeKit Areas.

A custom integration that manages one HomeKit Bridge (through the official
``homeassistant.components.homekit`` integration) per Home Assistant area.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .area_manager import AreaManager
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the HomeKit Areas integration from YAML (not supported)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a HomeKit Areas config entry."""
    _LOGGER.info("HomeKit Areas entry loaded: %s", entry.title)

    # Initialize AreaManager
    area_manager = AreaManager(hass)
    await area_manager.async_setup()

    # Store in hass.data for access by other components
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "area_manager": area_manager,
    }

    # Discover areas and log them
    areas = await area_manager.async_discover_areas()
    _LOGGER.info("Discovered %d areas:", len(areas))
    for area in areas:
        _LOGGER.info("  - %s (id: %s)", area.name, area.area_id)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a HomeKit Areas config entry."""
    # Shutdown AreaManager
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        area_manager = hass.data[DOMAIN][entry.entry_id]["area_manager"]
        await area_manager.async_shutdown()
        del hass.data[DOMAIN][entry.entry_id]

        # Clean up DOMAIN key if empty
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]

    return True
