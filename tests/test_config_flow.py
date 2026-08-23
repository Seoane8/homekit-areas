"""Tests for the HomeKit Areas config flow."""

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.homekit_areas import const


async def test_user_step_shows_form(hass: HomeAssistant) -> None:
    """The user step shows a form with area mode selector."""
    result = await hass.config_entries.flow.async_init(
        const.DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_user_step_all_areas_skips_to_port(hass: HomeAssistant) -> None:
    """Selecting 'all areas' skips the area selection step."""
    result = await hass.config_entries.flow.async_init(
        const.DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_AREA_MODE: const.AREA_MODE_ALL},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "port"


async def test_user_step_select_areas_shows_area_picker(hass: HomeAssistant) -> None:
    """Selecting 'select areas' shows the area picker step."""
    result = await hass.config_entries.flow.async_init(
        const.DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_AREA_MODE: const.AREA_MODE_SELECT},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "select_areas"


async def test_full_flow_all_areas(hass: HomeAssistant) -> None:
    """Test the complete flow with 'all areas' mode."""
    # Step 1: user - select all areas
    result = await hass.config_entries.flow.async_init(
        const.DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_AREA_MODE: const.AREA_MODE_ALL},
    )
    assert result["step_id"] == "port"

    # Step 2: port
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_INITIAL_PORT: 21070},
    )
    assert result["step_id"] == "domains"

    # Step 3: domains
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_DOMAINS: ["light", "switch"]},
    )
    assert result["step_id"] == "excluded"

    # Step 4: excluded entities
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_EXCLUDED_ENTITIES: []},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "HomeKit Areas"

    entry = result["result"]
    assert entry.options[const.CONF_AREA_MODE] == const.AREA_MODE_ALL
    assert entry.options[const.CONF_AREAS] == []
    assert entry.options[const.CONF_INITIAL_PORT] == 21070
    assert entry.options[const.CONF_DOMAINS] == ["light", "switch"]
    assert entry.options[const.CONF_EXCLUDED_ENTITIES] == []


async def test_full_flow_select_areas(hass: HomeAssistant) -> None:
    """Test the complete flow with specific areas selected."""
    # Create some test areas
    area_registry = hass.helpers.area_registry.async_get(hass)
    area1 = area_registry.async_create("Salón")
    area2 = area_registry.async_create("Cocina")
    area_registry.async_create("Dormitorio")

    # Step 1: user - select areas mode
    result = await hass.config_entries.flow.async_init(
        const.DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_AREA_MODE: const.AREA_MODE_SELECT},
    )
    assert result["step_id"] == "select_areas"

    # Step 2: select specific areas
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_AREAS: [area1.area_id, area2.area_id]},
    )
    assert result["step_id"] == "port"

    # Step 3: port
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_INITIAL_PORT: 21080},
    )
    assert result["step_id"] == "domains"

    # Step 4: domains
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_DOMAINS: list(const.DEFAULT_DOMAINS)},
    )
    assert result["step_id"] == "excluded"

    # Step 5: excluded entities
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_EXCLUDED_ENTITIES: []},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY

    entry = result["result"]
    assert entry.options[const.CONF_AREA_MODE] == const.AREA_MODE_SELECT
    assert set(entry.options[const.CONF_AREAS]) == {area1.area_id, area2.area_id}
    assert entry.options[const.CONF_INITIAL_PORT] == 21080


async def test_single_instance_aborts(hass: HomeAssistant) -> None:
    """A second config flow is aborted."""
    # Create first entry
    result = await hass.config_entries.flow.async_init(
        const.DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_AREA_MODE: const.AREA_MODE_ALL},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_INITIAL_PORT: 21070},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_DOMAINS: list(const.DEFAULT_DOMAINS)},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={const.CONF_EXCLUDED_ENTITIES: []},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY

    # Try to create second entry
    second = await hass.config_entries.flow.async_init(
        const.DOMAIN, context={"source": SOURCE_USER}
    )
    assert second["type"] is FlowResultType.ABORT
    assert second["reason"] == "single_instance_allowed"
