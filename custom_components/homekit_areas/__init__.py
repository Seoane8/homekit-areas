"""HomeKit Areas.

A custom integration that manages one HomeKit Bridge (through the official
``homeassistant.components.homekit`` integration) per Home Assistant area.
"""

from __future__ import annotations

import asyncio
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
from .port_manager import PortManager

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

    # Initialize PortManager for persistent port allocation
    port_manager = PortManager(hass, initial_port)
    await port_manager.async_load()

    # Check if initial port changed
    port_changed = (
        port_manager._saved_initial_port is not None
        and port_manager._saved_initial_port != initial_port
    )

    # Initialize BridgeManager with PortManager
    bridge_manager = BridgeManager(hass, port_manager)

    # Store in hass.data for access by other components
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "area_manager": area_manager,
        "entity_filter": entity_filter,
        "port_manager": port_manager,
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

    # Get list of area_ids we should have bridges for
    configured_area_ids = {area.area_id for area in areas_to_process}

    # Check if initial port changed
    if port_changed:
        _LOGGER.info(
            "Initial port changed from %d to %d, recreating bridges",
            port_manager._saved_initial_port,
            initial_port,
        )
        # Remove ALL existing bridges first (they have old ports)
        existing_bridges = bridge_manager.get_all_bridges()
        for area_id in list(existing_bridges.keys()):
            _LOGGER.info(
                "Removing bridge for area %s (port changed)",
                area_id,
            )
            await bridge_manager.remove_bridge(area_id)

        # Wait for all bridges to be fully removed
        await asyncio.sleep(1.0)

        # Reset port mappings after removing bridges
        port_manager.reset_all_ports(initial_port)
        await port_manager.async_save()
    else:
        # Port didn't change, preserve existing bridges
        _LOGGER.debug("Initial port unchanged, preserving existing bridges")
        # Remove bridges for areas that are no longer configured
        existing_bridges = bridge_manager.get_all_bridges()
        for area_id in list(existing_bridges.keys()):
            if area_id not in configured_area_ids:
                _LOGGER.info(
                    "Removing bridge for area %s (no longer configured)",
                    area_id,
                )
                await bridge_manager.remove_bridge(area_id)

    # Create bridges for configured areas
    for area in areas_to_process:
        area_id = area.area_id

        # Check if bridge already exists for this area
        if not port_changed and port_manager.has_port(area_id):
            _LOGGER.debug(
                "Bridge for area %s already exists, skipping creation",
                area_id,
            )
            continue

        _LOGGER.info("  - %s (id: %s)", area.name, area_id)

        # Get entities for this area and apply filter
        area_entities = await area_manager.async_get_entities_for_area(area_id)
        filtered_entities = entity_filter.filter_entities(area_entities)
        _LOGGER.info(
            "    Entities: %d total, %d after filtering",
            len(area_entities),
            len(filtered_entities),
        )

        # Update bridge with filtered entities
        # Port will be allocated by PortManager in create_bridge
        area.entities = filtered_entities

        # Create bridge for this area
        await bridge_manager.create_bridge(area)

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
