"""Area Manager for HomeKit Areas.

Manages discovery and tracking of Home Assistant areas, including
detection of new areas, removed areas, and name changes.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .models import AreaBridge

_LOGGER = logging.getLogger(__name__)

EVENT_AREA_REGISTRY_UPDATED = "area_registry_updated"
EVENT_ENTITY_REGISTRY_UPDATED = "entity_registry_updated"


class AreaManager:
    """Manage Home Assistant areas and their entities.

    Responsibilities:
    - Discover areas
    - Get area_id and names
    - Detect new areas
    - Detect removed areas
    - Detect name changes
    - Get entities associated with an area
    - Detect entity area changes
    - Detect new entities in areas
    """

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the AreaManager."""
        self.hass = hass
        self._area_registry = ar.async_get(hass)
        self._entity_registry = er.async_get(hass)
        self._device_registry = dr.async_get(hass)
        self._listeners: list[Callable[[], None]] = []
        self._known_areas: dict[str, str] = {}  # area_id -> name
        self._change_callbacks: list[Callable[[str, dict[str, Any]], None]] = []

    async def async_setup(self) -> None:
        """Set up the area manager and start listening for changes."""
        # Listen for area registry changes
        self._listeners.append(
            self.hass.bus.async_listen(
                EVENT_AREA_REGISTRY_UPDATED,
                self._async_handle_area_registry_update,
            )
        )

        # Listen for entity registry changes
        self._listeners.append(
            self.hass.bus.async_listen(
                EVENT_ENTITY_REGISTRY_UPDATED,
                self._async_handle_entity_registry_update,
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
                    self._notify_change(
                        "area_created",
                        {
                            "area_id": area_id,
                            "name": name,
                        },
                    )

        elif action == "remove":
            area_id = event.data.get("area_id")
            if area_id and area_id in self._known_areas:
                name = self._known_areas.pop(area_id)
                _LOGGER.info("Area removed: %s (%s)", name, area_id)
                self._notify_change(
                    "area_removed",
                    {
                        "area_id": area_id,
                        "name": name,
                    },
                )

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
                        self._notify_change(
                            "area_renamed",
                            {
                                "area_id": area_id,
                                "old_name": old_name,
                                "new_name": new_name,
                            },
                        )

    def register_change_callback(
        self, callback: Callable[[str, dict[str, Any]], None]
    ) -> None:
        """Register a callback to be notified of area/entity changes.

        The callback receives:
        - change_type: str (e.g., "entity_area_changed", "new_entity", "area_renamed")
        - data: dict with relevant information about the change
        """
        self._change_callbacks.append(callback)

    def _notify_change(self, change_type: str, data: dict[str, Any]) -> None:
        """Notify all registered callbacks about a change."""
        for cb in self._change_callbacks:
            try:
                cb(change_type, data)
            except Exception:
                _LOGGER.exception("Error in change callback for %s", change_type)

    async def async_shutdown(self) -> None:
        """Shut down the area manager."""
        for remove_listener in self._listeners:
            remove_listener()
        self._listeners.clear()
        self._change_callbacks.clear()

    def get_known_areas(self) -> dict[str, str]:
        """Return a copy of known areas (area_id -> name)."""
        return self._known_areas.copy()

    @callback
    def _async_handle_entity_registry_update(self, event: Event) -> None:
        """Handle entity registry updates."""
        action = event.data.get("action")
        entity_id = event.data.get("entity_id")

        if not entity_id:
            return

        if action == "update":
            changes = event.data.get("changes", {})

            # Check if area_id changed
            if "area_id" in changes:
                new_area_id = changes["area_id"]
                # Get old area from device or entity
                entity_entry = self._entity_registry.async_get(entity_id)
                old_area_id = None

                if entity_entry:
                    # Check if entity has direct area assignment
                    if entity_entry.area_id:
                        # The change was to the entity itself
                        old_area_id = changes.get("area_id")  # This is the old value
                    elif entity_entry.device_id:
                        # Check device area
                        device_entry = self._device_registry.async_get(
                            entity_entry.device_id
                        )
                        if device_entry:
                            old_area_id = device_entry.area_id

                # The new area is what's in the registry now
                if entity_entry and entity_entry.area_id:
                    new_area_id = entity_entry.area_id
                elif entity_entry and entity_entry.device_id:
                    device_entry = self._device_registry.async_get(
                        entity_entry.device_id
                    )
                    if device_entry:
                        new_area_id = device_entry.area_id

                if old_area_id != new_area_id:
                    _LOGGER.info(
                        "Entity %s moved from area %s to %s",
                        entity_id,
                        old_area_id,
                        new_area_id,
                    )
                    self._notify_change(
                        "entity_area_changed",
                        {
                            "entity_id": entity_id,
                            "old_area_id": old_area_id,
                            "new_area_id": new_area_id,
                        },
                    )

        elif action == "create":
            # New entity created - check if it belongs to a managed area
            entity_entry = self._entity_registry.async_get(entity_id)
            if entity_entry:
                area_id = None
                if entity_entry.area_id:
                    area_id = entity_entry.area_id
                elif entity_entry.device_id:
                    device_entry = self._device_registry.async_get(
                        entity_entry.device_id
                    )
                    if device_entry:
                        area_id = device_entry.area_id

                if area_id and area_id in self._known_areas:
                    _LOGGER.info(
                        "New entity %s detected in area %s",
                        entity_id,
                        area_id,
                    )
                    self._notify_change(
                        "new_entity",
                        {
                            "entity_id": entity_id,
                            "area_id": area_id,
                        },
                    )
