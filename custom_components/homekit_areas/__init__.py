"""HomeKit Areas.

A custom integration that manages one HomeKit Bridge (through the official
``homeassistant.components.homekit`` integration) per Home Assistant area.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .area_manager import AreaManager
from .bridge_manager import BridgeManager
from .const import (
    CONF_AREAS,
    CONF_DOMAINS,
    CONF_EXCLUDED_ENTITIES,
    CONF_INITIAL_PORT,
    DEFAULT_DOMAINS,
    DEFAULT_INITIAL_PORT,
    DOMAIN,
)
from .entity_filter import EntityFilter

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the HomeKit Areas integration from YAML (not supported)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a HomeKit Areas config entry."""
    _LOGGER.info("HomeKit Areas entry loaded: %s", entry.title)

    # Get configuration
    areas = entry.options.get(CONF_AREAS, [])
    domains = entry.options.get(CONF_DOMAINS, list(DEFAULT_DOMAINS))
    excluded_entities = entry.options.get(CONF_EXCLUDED_ENTITIES, [])
    initial_port = entry.options.get(CONF_INITIAL_PORT, DEFAULT_INITIAL_PORT)

    # Initialize AreaManager
    area_manager = AreaManager(hass)
    await area_manager.async_setup()

    # Initialize EntityFilter
    entity_filter = EntityFilter(
        hass=hass,
        allowed_domains=domains,
        excluded_entities=excluded_entities,
    )

    # Initialize BridgeManager
    bridge_manager = BridgeManager(hass)

    # Clean up any stale bridges from previous attempts
    await bridge_manager.cleanup_stale_bridges()

    # Store in hass.data for access by other components
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "area_manager": area_manager,
        "entity_filter": entity_filter,
        "bridge_manager": bridge_manager,
        "config": {
            "areas": areas,
            "domains": domains,
            "excluded_entities": excluded_entities,
            "initial_port": initial_port,
        },
    }

    # Discover areas and create bridges
    discovered_areas = await area_manager.async_discover_areas()
    _LOGGER.info("Discovered %d areas total", len(discovered_areas))

    # Filter areas based on configuration
    if areas:
        # Only create bridges for selected areas
        areas_to_process = [area for area in discovered_areas if area.area_id in areas]
        _LOGGER.info(
            "Creating bridges for %d selected areas: %s",
            len(areas_to_process),
            areas,
        )
    else:
        # Create bridges for all areas
        areas_to_process = discovered_areas
        _LOGGER.info("Creating bridges for all %d areas", len(areas_to_process))

    current_port = initial_port
    for area in areas_to_process:
        _LOGGER.info("  - %s (id: %s)", area.name, area.area_id)

        # Get entities for this area and apply filter
        area_entities = await area_manager.async_get_entities_for_area(area.area_id)
        filtered_entities = entity_filter.filter_entities(area_entities)
        _LOGGER.info(
            "    Entities: %d total, %d after filtering",
            len(area_entities),
            len(filtered_entities),
        )

        # Update bridge with filtered entities and port
        area.port = current_port
        area.entities = filtered_entities

        # Create bridge for this area
        await bridge_manager.create_bridge(area)
        current_port += 1

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a HomeKit Areas config entry."""
    # Shutdown AreaManager
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        data = hass.data[DOMAIN][entry.entry_id]
        area_manager = data.get("area_manager")
        if area_manager:
            await area_manager.async_shutdown()
        del hass.data[DOMAIN][entry.entry_id]

        # Clean up DOMAIN key if empty
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]

    return True
