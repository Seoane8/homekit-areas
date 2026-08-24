"""Bridge Manager for HomeKit Areas.

Manages the lifecycle of HomeKit bridges (ConfigEntry-s del dominio `homekit`)
for each area. Creates, starts, stops, and updates bridges using the official
HomeKit integration.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.core import HomeAssistant

from .const import HOMEKIT_DOMAIN
from .models import AreaBridge
from .port_manager import PortManager

_LOGGER = logging.getLogger(__name__)

# HomeKit ConfigEntry data keys (from official integration)
CONF_NAME = "name"
CONF_PORT = "port"
CONF_HOMEKIT_MODE = "mode"
CONF_FILTER = "filter"
CONF_EXCLUDE_ACCESSORY_MODE = "exclude_accessory_mode"
CONF_ENTITY_CONFIG = "entity_config"
CONF_DEVICES = "devices"

HOMEKIT_MODE_BRIDGE = "bridge"


class BridgeManager:
    """Manage HomeKit bridges for areas.

    Responsibilities:
    - create_bridge(): Create a HomeKit ConfigEntry for an area
    - start_bridge(): Start a bridge (implicit in creation)
    - stop_bridge(): Stop a bridge
    - update_bridge(): Update bridge entities

    Does NOT:
    - Discover areas (AreaManager does this)
    - Decide which entities belong to each area (EntityFilter does this)
    - Manage user configuration (ConfigFlow does this)
    """

    def __init__(self, hass: HomeAssistant, port_manager: PortManager) -> None:
        """Initialize the BridgeManager.

        Args:
            hass: Home Assistant instance
            port_manager: PortManager for persistent port allocation
        """
        self.hass = hass
        self.port_manager = port_manager
        # Mapping: area_id -> {entry_id, port}
        self._bridge_registry: dict[str, dict[str, Any]] = {}

    async def cleanup_stale_bridges(self) -> None:
        """Remove all HomeKit bridges created by this integration.

        This cleans up ConfigEntry-s del dominio `homekit` que fueron creados
        en intentos anteriores y que pueden estar ocupando puertos/nombres.
        """
        _LOGGER.info("Cleaning up stale HomeKit bridges...")
        entries_to_remove = []

        for entry in self.hass.config_entries.async_entries(HOMEKIT_DOMAIN):
            # Check if this entry was created by us (name starts with "HomeKit ")
            entry_name = entry.data.get(CONF_NAME, "")
            if entry_name.startswith("HomeKit "):
                entries_to_remove.append(entry)

        for entry in entries_to_remove:
            _LOGGER.info(
                "Removing stale bridge: %s (entry_id=%s)",
                entry.data.get(CONF_NAME),
                entry.entry_id,
            )
            await self.hass.config_entries.async_remove(entry.entry_id)

        _LOGGER.info("Cleaned up %d stale bridges", len(entries_to_remove))

    async def create_bridge(self, bridge: AreaBridge) -> None:
        """Create a HomeKit bridge for an area.

        Creates a ConfigEntry in the `homekit` domain with the appropriate
        configuration. The bridge will start automatically after creation.

        Args:
            bridge: AreaBridge object with area_id, name, port, and entities
        """
        area_id = bridge.area_id
        name = bridge.name
        entities = bridge.entities

        # Get or allocate port from PortManager
        port = self.port_manager.allocate_port(area_id)
        bridge.port = port  # Update bridge with allocated port

        _LOGGER.info(
            "Creating bridge for area %s: %s (port %d, %d entities)",
            area_id,
            name,
            port,
            len(entities),
        )

        # Build HomeKit ConfigEntry data
        data = {
            CONF_NAME: name,
            CONF_PORT: port,
            CONF_HOMEKIT_MODE: HOMEKIT_MODE_BRIDGE,
            CONF_EXCLUDE_ACCESSORY_MODE: True,
            CONF_FILTER: {
                "include_entities": list(entities),
            },
            CONF_ENTITY_CONFIG: {},
            CONF_DEVICES: [],
        }

        # Create ConfigEntry via flow
        result = await self.hass.config_entries.flow.async_init(
            HOMEKIT_DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=data,
        )

        if result["type"] == "create_entry":
            entry_id = result["result"].entry_id
            self._bridge_registry[area_id] = {
                "entry_id": entry_id,
                "port": port,
            }
            # Save port mapping to persistent storage
            await self.port_manager.async_save()
            _LOGGER.info(
                "Bridge created for area %s: entry_id=%s",
                area_id,
                entry_id,
            )
        else:
            _LOGGER.error(
                "Failed to create bridge for area %s: %s",
                area_id,
                result,
            )

    async def start_bridge(self, area_id: str) -> None:
        """Start a HomeKit bridge for an area.

        Bridges start automatically after creation, but this method can be
        used to explicitly restart a stopped bridge.

        Args:
            area_id: The area ID of the bridge to start
        """
        if area_id not in self._bridge_registry:
            _LOGGER.warning("Cannot start bridge: area %s not found", area_id)
            return

        entry_id = self._bridge_registry[area_id]["entry_id"]
        entry = self.hass.config_entries.async_get_entry(entry_id)

        if entry is None:
            _LOGGER.error("ConfigEntry %s not found for area %s", entry_id, area_id)
            return

        # Reload the entry to start it
        await self.hass.config_entries.async_reload(entry_id)
        _LOGGER.info("Bridge started for area %s", area_id)

    async def stop_bridge(self, area_id: str) -> None:
        """Stop a HomeKit bridge for an area.

        Unloads the ConfigEntry, stopping the bridge and freeing the port.

        Args:
            area_id: The area ID of the bridge to stop
        """
        if area_id not in self._bridge_registry:
            _LOGGER.warning("Cannot stop bridge: area %s not found", area_id)
            return

        entry_id = self._bridge_registry[area_id]["entry_id"]

        # Unload the entry
        await self.hass.config_entries.async_unload(entry_id)
        _LOGGER.info("Bridge stopped for area %s", area_id)

    async def update_bridge(self, bridge: AreaBridge) -> None:
        """Update a HomeKit bridge for an area.

        Updates the entity filter and reloads the bridge. Preserves pairing
        and port assignment.

        Args:
            bridge: AreaBridge object with updated entities
        """
        area_id = bridge.area_id

        if area_id not in self._bridge_registry:
            _LOGGER.warning("Cannot update bridge: area %s not found", area_id)
            return

        entry_id = self._bridge_registry[area_id]["entry_id"]
        entry = self.hass.config_entries.async_get_entry(entry_id)

        if entry is None:
            _LOGGER.error("ConfigEntry %s not found for area %s", entry_id, area_id)
            return

        entities = bridge.entities

        _LOGGER.info(
            "Updating bridge for area %s: %d entities",
            area_id,
            len(entities),
        )

        # Update options with new entity filter
        new_options = {
            **entry.options,
            CONF_FILTER: {
                "include_entities": list(entities),
            },
        }

        self.hass.config_entries.async_update_entry(entry, options=new_options)

        # Reload to apply changes
        await self.hass.config_entries.async_reload(entry_id)
        _LOGGER.info("Bridge updated for area %s", area_id)

    async def remove_bridge(self, area_id: str) -> None:
        """Remove a HomeKit bridge for an area.

        Removes the ConfigEntry and cleans up the registry.
        The port is released but NOT reused in V1.

        Args:
            area_id: The area ID of the bridge to remove
        """
        if area_id not in self._bridge_registry:
            _LOGGER.warning("Cannot remove bridge: area %s not found", area_id)
            return

        entry_id = self._bridge_registry[area_id]["entry_id"]

        # Remove the entry
        await self.hass.config_entries.async_remove(entry_id)

        # Clean up registry
        del self._bridge_registry[area_id]

        # Release port (but it will NOT be reused in V1)
        self.port_manager.release_port(area_id)
        await self.port_manager.async_save()

        _LOGGER.info("Bridge removed for area %s", area_id)

    def get_bridge_info(self, area_id: str) -> dict[str, Any] | None:
        """Get bridge information for an area.

        Args:
            area_id: The area ID

        Returns:
            Dict with entry_id and port, or None if not found
        """
        return self._bridge_registry.get(area_id)

    def get_all_bridges(self) -> dict[str, dict[str, Any]]:
        """Get all registered bridges.

        Returns:
            Dict mapping area_id to bridge info
        """
        return self._bridge_registry.copy()
