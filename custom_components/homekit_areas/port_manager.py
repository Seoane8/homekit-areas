"""Port Manager for HomeKit Areas.

Manages persistent port allocation for HomeKit bridges per area.
Ports are assigned once and never reused, even if the area is removed.
"""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = f"{DOMAIN}_port_mapping"
STORAGE_VERSION = 1


class PortManager:
    """Manage persistent port allocation for HomeKit bridges.

    Responsibilities:
    - Persist area_id → port mapping across restarts
    - Allocate new ports for new areas
    - Never reuse ports from removed areas
    - Maintain stable port assignments
    """

    def __init__(self, hass: HomeAssistant, initial_port: int) -> None:
        """Initialize the PortManager.

        Args:
            hass: Home Assistant instance
            initial_port: Starting port for new allocations (default 21070)
        """
        self.hass = hass
        self._initial_port = initial_port
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        # Mapping: area_id → port
        self._port_mapping: dict[str, int] = {}
        # Track next available port
        self._next_port = initial_port
        # Track the initial port that was used when mapping was created
        self._saved_initial_port: int | None = None

    async def async_load(self) -> None:
        """Load port mapping from storage."""
        data = await self._store.async_load()
        if data:
            self._port_mapping = data.get("port_mapping", {})
            self._next_port = data.get("next_port", self._initial_port)
            self._saved_initial_port = data.get("saved_initial_port")
            _LOGGER.info(
                "Loaded port mapping: %d areas, next port: %d, saved initial port: %s",
                len(self._port_mapping),
                self._next_port,
                self._saved_initial_port,
            )
            # Check if initial port has changed (but don't reset yet)
            if (
                self._saved_initial_port is not None
                and self._saved_initial_port != self._initial_port
            ):
                _LOGGER.info(
                    "Initial port changed from %d to %d (reset will be handled by caller)",
                    self._saved_initial_port,
                    self._initial_port,
                )
        else:
            _LOGGER.info("No existing port mapping found, starting fresh")
            self._port_mapping = {}
            self._next_port = self._initial_port
            self._saved_initial_port = self._initial_port

    async def async_save(self) -> None:
        """Save port mapping to storage."""
        data = {
            "port_mapping": self._port_mapping,
            "next_port": self._next_port,
            "saved_initial_port": self._initial_port,
        }
        await self._store.async_save(data)
        _LOGGER.debug("Saved port mapping: %d areas", len(self._port_mapping))

    def get_port(self, area_id: str) -> int | None:
        """Get the port assigned to an area.

        Args:
            area_id: The area ID

        Returns:
            The port number, or None if not assigned
        """
        return self._port_mapping.get(area_id)

    def allocate_port(self, area_id: str) -> int:
        """Allocate a port for an area.

        If the area already has a port, returns the existing port.
        Otherwise, allocates the next available port.

        Args:
            area_id: The area ID

        Returns:
            The allocated port number
        """
        # Check if area already has a port
        if area_id in self._port_mapping:
            port = self._port_mapping[area_id]
            _LOGGER.debug("Area %s already has port %d", area_id, port)
            return port

        # Allocate next available port
        port = self._next_port
        self._port_mapping[area_id] = port
        self._next_port += 1

        _LOGGER.info("Allocated port %d for area %s", port, area_id)
        return port

    def release_port(self, area_id: str) -> None:
        """Release the port for an area.

        The port is NOT reused in V1. It remains marked as used.

        Args:
            area_id: The area ID
        """
        if area_id in self._port_mapping:
            port = self._port_mapping[area_id]
            del self._port_mapping[area_id]
            _LOGGER.info(
                "Released port %d for area %s (port will not be reused)",
                port,
                area_id,
            )
            # Note: We do NOT decrement _next_port or add port to a free list
            # This ensures ports are never reused in V1

    def get_all_mappings(self) -> dict[str, int]:
        """Get all port mappings.

        Returns:
            Dict mapping area_id to port
        """
        return self._port_mapping.copy()

    def has_port(self, area_id: str) -> bool:
        """Check if an area has a port allocated.

        Args:
            area_id: The area ID

        Returns:
            True if the area has a port, False otherwise
        """
        return area_id in self._port_mapping

    def reset_all_ports(self, new_initial_port: int) -> None:
        """Reset all port mappings and start from a new initial port.

        This clears all existing mappings and resets the next port counter.
        Used when the user changes the initial port in configuration.

        Args:
            new_initial_port: The new starting port
        """
        _LOGGER.info(
            "Resetting all ports. Old mapping: %s, new initial port: %d",
            self._port_mapping,
            new_initial_port,
        )
        self._port_mapping = {}
        self._next_port = new_initial_port
        self._saved_initial_port = new_initial_port
        self._initial_port = new_initial_port
