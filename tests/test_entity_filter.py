"""Tests for EntityFilter."""

from unittest.mock import MagicMock

import pytest

from custom_components.homekit_areas.entity_filter import EntityFilter


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance."""
    hass = MagicMock()
    hass.data = {}
    return hass


@pytest.fixture
def entity_filter(mock_hass):
    """Create an EntityFilter instance."""
    return EntityFilter(
        hass=mock_hass,
        allowed_domains=["light", "switch", "fan", "cover"],
        excluded_entities=["light.excluded_light"],
    )


def test_filter_by_domain(entity_filter):
    """Test filtering by allowed domains."""
    entities = {
        "light.living_room",
        "switch.kitchen",
        "sensor.temperature",
        "fan.bedroom",
        "cover.garage",
        "climate.hvac",
    }

    filtered = entity_filter._filter_by_domain(entities)

    assert filtered == {
        "light.living_room",
        "switch.kitchen",
        "fan.bedroom",
        "cover.garage",
    }


def test_filter_excluded(entity_filter):
    """Test filtering excluded entities."""
    entities = {
        "light.living_room",
        "light.excluded_light",
        "switch.kitchen",
    }

    filtered = entity_filter._filter_excluded(entities)

    assert filtered == {
        "light.living_room",
        "switch.kitchen",
    }


def test_filter_unsupported(entity_filter):
    """Test filtering unsupported domains."""
    entities = {
        "light.living_room",
        "update.firmware",
        "select.option",
        "button.restart",
        "switch.kitchen",
    }

    filtered = entity_filter._filter_unsupported(entities)

    assert filtered == {
        "light.living_room",
        "switch.kitchen",
    }


def test_filter_entities_pipeline(entity_filter):
    """Test the complete filtering pipeline."""
    entities = {
        "light.living_room",
        "light.excluded_light",  # Excluded
        "switch.kitchen",
        "sensor.temperature",  # Not in allowed domains
        "update.firmware",  # Unsupported
        "fan.bedroom",
        "cover.garage",
        "select.option",  # Unsupported
    }

    filtered = entity_filter.filter_entities(entities)

    assert filtered == {
        "light.living_room",
        "switch.kitchen",
        "fan.bedroom",
        "cover.garage",
    }


def test_filter_empty_set(entity_filter):
    """Test filtering an empty set."""
    filtered = entity_filter.filter_entities(set())
    assert filtered == set()


def test_filter_all_excluded(entity_filter):
    """Test when all entities are excluded."""
    entities = {"light.excluded_light"}
    filtered = entity_filter.filter_entities(entities)
    assert filtered == set()


def test_filter_no_allowed_domains(mock_hass):
    """Test with no allowed domains."""
    entity_filter = EntityFilter(
        hass=mock_hass,
        allowed_domains=[],
        excluded_entities=[],
    )

    entities = {"light.living_room", "switch.kitchen"}
    filtered = entity_filter.filter_entities(entities)

    assert filtered == set()


def test_filter_all_domains_allowed(mock_hass):
    """Test when all domains are allowed."""
    entity_filter = EntityFilter(
        hass=mock_hass,
        allowed_domains=["light", "switch", "sensor", "update"],
        excluded_entities=[],
    )

    entities = {
        "light.living_room",
        "switch.kitchen",
        "sensor.temperature",
        "update.firmware",  # Still filtered as unsupported
    }
    filtered = entity_filter.filter_entities(entities)

    assert filtered == {
        "light.living_room",
        "switch.kitchen",
        "sensor.temperature",
    }


def test_get_filtered_entities_for_area(entity_filter):
    """Test convenience method for area filtering."""
    area_entities = {
        "light.living_room",
        "light.excluded_light",
        "switch.kitchen",
    }

    filtered = entity_filter.get_filtered_entities_for_area(area_entities)

    assert filtered == {
        "light.living_room",
        "switch.kitchen",
    }


def test_filter_preserves_entity_format(entity_filter):
    """Test that entity format is preserved."""
    entities = {
        "light.living_room_main",
        "light.bedroom_1",
        "switch.kitchen_2",
    }

    filtered = entity_filter.filter_entities(entities)

    # Verify format is preserved
    for entity_id in filtered:
        assert "." in entity_id
        domain, object_id = entity_id.split(".", 1)
        assert domain in ["light", "switch"]
        assert "_" in object_id or object_id.isalnum()
