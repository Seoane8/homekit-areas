"""Config flow for HomeKit Areas."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries

from .const import (
    CONF_AREAS,
    CONF_DOMAINS,
    CONF_EXCLUDED_ENTITIES,
    CONF_INITIAL_PORT,
    DEFAULT_DOMAINS,
    DEFAULT_INITIAL_PORT,
    DOMAIN,
)


class HomeKitAreasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HomeKit Areas."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial user step.

        Phase 1 only creates the config entry with sane defaults. The full
        UI (areas, port, domains, excluded entities) is added in Phase 2.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="HomeKit Areas",
                data={},
                options={
                    CONF_AREAS: [],
                    CONF_INITIAL_PORT: DEFAULT_INITIAL_PORT,
                    CONF_DOMAINS: list(DEFAULT_DOMAINS),
                    CONF_EXCLUDED_ENTITIES: [],
                },
            )

        return self.async_show_form(step_id="user")
