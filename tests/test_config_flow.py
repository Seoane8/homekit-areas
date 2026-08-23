"""Tests for the HomeKit Areas config flow."""

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.homekit_areas import const


async def test_user_form_shown(hass: HomeAssistant) -> None:
    """The user step shows a form when no input is provided."""
    result = await hass.config_entries.flow.async_init(
        const.DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_user_creates_entry_with_defaults(hass: HomeAssistant) -> None:
    """Submitting the user step creates an entry populated with defaults."""
    result = await hass.config_entries.flow.async_init(
        const.DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "HomeKit Areas"

    entry = result["result"]
    assert entry.data == {}
    assert entry.options[const.CONF_AREAS] == []
    assert entry.options[const.CONF_INITIAL_PORT] == const.DEFAULT_INITIAL_PORT
    assert entry.options[const.CONF_DOMAINS] == list(const.DEFAULT_DOMAINS)
    assert entry.options[const.CONF_EXCLUDED_ENTITIES] == []


async def test_single_instance_aborts(hass: HomeAssistant) -> None:
    """A second config flow is aborted."""
    await hass.config_entries.flow.async_init(
        const.DOMAIN,
        context={"source": SOURCE_USER},
        data={},
    )

    second = await hass.config_entries.flow.async_init(
        const.DOMAIN, context={"source": SOURCE_USER}
    )
    assert second["type"] is FlowResultType.ABORT
    assert second["reason"] == "single_instance_allowed"
