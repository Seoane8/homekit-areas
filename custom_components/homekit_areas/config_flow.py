"""Config flow for HomeKit Areas."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import selector

from .const import (
    AREA_MODE_ALL,
    AREA_MODE_SELECT,
    CONF_AREA_MODE,
    CONF_AREAS,
    CONF_DOMAINS,
    CONF_EXCLUDED_ENTITIES,
    CONF_INITIAL_PORT,
    DEFAULT_DOMAINS,
    DEFAULT_INITIAL_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

SUPPORTED_DOMAINS = [
    "light",
    "switch",
    "fan",
    "cover",
    "climate",
    "lock",
    "media_player",
    "binary_sensor",
    "sensor",
    "vacuum",
    "water_heater",
    "humidifier",
    "alarm_control_panel",
    "camera",
    "scene",
    "script",
    "input_boolean",
    "input_select",
    "select",
    "button",
    "automation",
    "remote",
    "lawn_mower",
    "valve",
]


class HomeKitAreasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HomeKit Areas."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._config: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the area selection step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            area_mode = user_input.get(CONF_AREA_MODE, AREA_MODE_ALL)
            self._config[CONF_AREA_MODE] = area_mode
            if area_mode == AREA_MODE_SELECT:
                return await self.async_step_select_areas()
            else:
                self._config[CONF_AREAS] = []
                return await self.async_step_port()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_AREA_MODE, default=AREA_MODE_ALL): vol.In(
                        {
                            AREA_MODE_ALL: "Todas las áreas",
                            AREA_MODE_SELECT: "Seleccionar áreas",
                        }
                    ),
                }
            ),
        )

    async def async_step_select_areas(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the area selection step when 'select' mode is chosen."""
        if user_input is not None:
            self._config[CONF_AREAS] = user_input.get(CONF_AREAS, [])
            return await self.async_step_port()

        # Get all areas from Home Assistant
        area_reg = ar.async_get(self.hass)
        areas = area_reg.async_list_areas()

        _LOGGER.debug("Found %d areas in registry", len(areas))

        area_options = [
            selector.SelectOptionDict(
                value=area.area_id, label=area.name or area.area_id
            )
            for area in sorted(areas, key=lambda a: a.name or a.area_id)
        ]

        _LOGGER.debug("Area options: %s", area_options)

        return self.async_show_form(
            step_id="select_areas",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_AREAS): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=area_options,
                            multiple=True,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_port(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the port configuration step."""
        if user_input is not None:
            self._config[CONF_INITIAL_PORT] = user_input[CONF_INITIAL_PORT]
            return await self.async_step_domains()

        return self.async_show_form(
            step_id="port",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_INITIAL_PORT, default=DEFAULT_INITIAL_PORT
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1024,
                            max=65535,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
        )

    async def async_step_domains(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the domain selection step."""
        if user_input is not None:
            self._config[CONF_DOMAINS] = user_input.get(CONF_DOMAINS, [])
            return await self.async_step_excluded()

        return self.async_show_form(
            step_id="domains",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DOMAINS, default=list(DEFAULT_DOMAINS)
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(value=domain, label=domain)
                                for domain in SUPPORTED_DOMAINS
                            ],
                            multiple=True,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_excluded(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the excluded entities step."""
        if user_input is not None:
            self._config[CONF_EXCLUDED_ENTITIES] = user_input.get(
                CONF_EXCLUDED_ENTITIES, []
            )
            return self.async_create_entry(
                title="HomeKit Areas",
                data={},
                options=self._config,
            )

        return self.async_show_form(
            step_id="excluded",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_EXCLUDED_ENTITIES, default=[]): (
                        selector.EntitySelector(
                            selector.EntitySelectorConfig(
                                domain=self._config.get(CONF_DOMAINS, []),
                                multiple=True,
                            )
                        )
                    ),
                }
            ),
        )
