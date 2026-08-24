"""Entity Filter for HomeKit Areas.

Filters entities based on domains, exclusions, and HomeKit compatibility.
"""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, split_entity_id
from homeassistant.helpers import entity_registry as er

_LOGGER = logging.getLogger(__name__)

# Domains that are not supported by HomeKit
UNSUPPORTED_DOMAINS = {
    "update",
    "select",
    "button",
    "input_button",
    "scene",
    "script",
    "automation",
    "person",
    "zone",
    "timer",
    "counter",
    "input_datetime",
    "input_number",
    "input_text",
    "input_select",
    "number",
    "text",
    "datetime",
    "tts",
    "weather",
    "calendar",
    "todo",
    "stt",
    "notify",
    "conversation",
    "device_tracker",
    "geo_location",
    "sun",
    "persistent_notification",
    "history",
    "logbook",
    "map",
    "media_source",
    "backup",
    "hardware",
    "system_health",
    "analytics",
    "bluetooth",
    "dhcp",
    "ssdp",
    "usb",
    "zeroconf",
    "hassio",
    "cloud",
    "mobile_app",
    "tag",
    "qrcode",
}


class EntityFilter:
    """Filter entities for HomeKit bridges.

    Pipeline:
    1. Get entities for the area
    2. Filter by allowed domains
    3. Filter out excluded entities
    4. Filter out unsupported domains
    """

    def __init__(
        self,
        hass: HomeAssistant,
        allowed_domains: list[str],
        excluded_entities: list[str],
    ) -> None:
        """Initialize the EntityFilter.

        Args:
            hass: Home Assistant instance
            allowed_domains: List of domains to include (e.g., ["light", "switch"])
            excluded_entities: List of specific entity_ids to exclude
        """
        self.hass = hass
        self.allowed_domains = set(allowed_domains)
        self.excluded_entities = set(excluded_entities)
        self._entity_registry = er.async_get(hass)

    def filter_entities(self, entity_ids: set[str]) -> set[str]:
        """Filter a set of entity_ids through the pipeline.

        Args:
            entity_ids: Set of entity_ids to filter

        Returns:
            Set of entity_ids that pass all filters
        """
        filtered = set(entity_ids)

        # Step 1: Filter by allowed domains
        filtered = self._filter_by_domain(filtered)

        # Step 2: Filter out excluded entities
        filtered = self._filter_excluded(filtered)

        # Step 3: Filter out unsupported domains
        filtered = self._filter_unsupported(filtered)

        return filtered

    def _filter_by_domain(self, entity_ids: set[str]) -> set[str]:
        """Keep only entities from allowed domains."""
        filtered = set()
        for entity_id in entity_ids:
            domain = split_entity_id(entity_id)[0]
            if domain in self.allowed_domains:
                filtered.add(entity_id)
        return filtered

    def _filter_excluded(self, entity_ids: set[str]) -> set[str]:
        """Remove excluded entities."""
        return entity_ids - self.excluded_entities

    def _filter_unsupported(self, entity_ids: set[str]) -> set[str]:
        """Remove entities from unsupported domains."""
        filtered = set()
        for entity_id in entity_ids:
            domain = split_entity_id(entity_id)[0]
            if domain not in UNSUPPORTED_DOMAINS:
                filtered.add(entity_id)
        return filtered

    def get_filtered_entities_for_area(self, area_entities: set[str]) -> set[str]:
        """Get filtered entities for a specific area.

        This is a convenience method that applies the full filter pipeline
        to entities from a specific area.

        Args:
            area_entities: Set of entity_ids from the area

        Returns:
            Set of filtered entity_ids
        """
        return self.filter_entities(area_entities)
