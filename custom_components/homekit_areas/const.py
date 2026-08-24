"""Constants for the HomeKit Areas integration."""

from __future__ import annotations

DOMAIN = "homekit_areas"
HOMEKIT_DOMAIN = "homekit"
PLATFORMS: list[str] = []

VERSION = "0.1.0"

# --- Config / option keys ---

# List of area ids managed by this entry. An empty list means "all areas".
CONF_AREAS = "areas"
# Mode for area selection: "all" or "select"
CONF_AREA_MODE = "area_mode"
AREA_MODE_ALL = "all"
AREA_MODE_SELECT = "select"
# Starting port for the per-area HomeKit bridges.
CONF_INITIAL_PORT = "initial_port"
# Domains allowed on the bridges.
CONF_DOMAINS = "domains"
# Entities explicitly excluded from every bridge.
CONF_EXCLUDED_ENTITIES = "excluded_entities"

# --- Defaults ---

DEFAULT_INITIAL_PORT = 21070
DEFAULT_DOMAINS = ("light", "switch", "fan", "cover")
