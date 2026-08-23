"""Area Manager for HomeKit Areas.

Manages discovery and tracking of Home Assistant areas, including
detection of new areas, removed areas, and name changes.
"""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import Event

from .models import AreaBridge

_LOGGER = logging.getLogger(__name__)

EVENT_AREA_REGISTRY_UPDATED = "area_registry_updated"


class AreaManager:
    """Manage Home Assistant areas and their entities.

    Responsibilities:
    - Discover areas
    - Get area_id and names
    - Detect new areas
    - Detect removed areas
    - Detect name changes
    - Get entities associated with an area
    """

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the AreaManager."""
        self.hass = hass
        self._area_registry = ar.async_get(hass)
        self._entity_registry = er.async_get(hass)
        self._device_registry = dr.async_get(hass)
        self._listeners: list[callback] = []
        self._known_areas: dict[str, str] = {}  # area_id -> name

    async def async_setup(self) -> None:
        """Set up the area manager and start listening for changes."""
        # Listen for area registry changes
        self._listeners.append(
            self.hass.bus.async_listen(
                EVENT_AREA_REGISTRY_UPDATED,
                self._async_handle_area_registry_update,
            )
        )

        # Initial discovery
        await self.async_discover_areas()

    async def async_discover_areas(self) -> list[AreaBridge]:
        """Discover all areas and return them as AreaBridge objects."""
        areas = self._area_registry.async_list_areas()
        area_bridges = []

        for area in areas:
            area_id = area.id
            name = area.name or area_id

            # Update known areas
            self._known_areas[area_id] = name

            # Create AreaBridge (entities will be populated later by EntityFilter)
            bridge = AreaBridge(
                area_id=area_id,
                name=f"HomeKit {name}",
                port=0,  # Will be assigned by BridgeManager
                entities=set(),
            )
            area_bridges.append(bridge)

        _LOGGER.debug("Discovered %d areas", len(area_bridges))
        return area_bridges

    async def async_get_entities_for_area(self, area_id: str) -> set[str]:
        """Get all entity_ids associated with an area.

        An entity is associated with an area if:
        - The entity itself has area_id set, OR
        - The entity's device has area_id set
        """
        entities = set()

        # Get entities directly assigned to the area
        for entity_entry in self._entity_registry.entities.values():
            if entity_entry.area_id == area_id:
                entities.add(entity_entry.entity_id)
            elif entity_entry.device_id:
                # Check if the device is in this area
                device_entry = self._device_registry.async_get(entity_entry.device_id)
                if device_entry and device_entry.area_id == area_id:
                    entities.add(entity_entry.entity_id)

        _LOGGER.debug("Found %d entities for area %s", len(entities), area_id)
        return entities

    @callback
    def _async_handle_area_registry_update(self, event: Event) -> None:
        """Handle area registry updates."""
        action = event.data.get("action")

        if action == "create":
            area_id = event.data.get("area_id")
            if area_id:
                area = self._area_registry.async_get_area(area_id)
                if area:
                    name = area.name or area_id
                    self._known_areas[area_id] = name
                    _LOGGER.info("New area detected: %s (%s)", name, area_id)

        elif action == "remove":
            area_id = event.data.get("area_id")
            if area_id and area_id in self._known_areas:
                name = self._known_areas.pop(area_id)
                _LOGGER.info("Area removed: %s (%s)", name, area_id)

        elif action == "update":
            area_id = event.data.get("area_id")
            if area_id:
                area = self._area_registry.async_get_area(area_id)
                if area:
                    old_name = self._known_areas.get(area_id)
                    new_name = area.name or area_id
                    if old_name != new_name:
                        self._known_areas[area_id] = new_name
                        _LOGGER.info(
                            "Area renamed: %s -> %s (%s)",
                            old_name,
                            new_name,
                            area_id,
                        )

    async def async_shutdown(self) -> None:
        """Shut down the area manager."""
        for remove_listener in self._listeners:
            remove_listener()
        self._listeners.clear()

    def get_known_areas(self) -> dict[str, str]:
        """Return a copy of known areas (area_id -> name)."""
        return self._known_areas.copy()
