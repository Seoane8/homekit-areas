"""Data models for HomeKit Areas."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AreaBridge:
    """Represent a HomeKit bridge for a specific area.

    The identity of the bridge is always the `area_id`, never the name.
    """

    area_id: str
    name: str
    port: int
    entities: set[str] = field(default_factory=set)

    def __hash__(self) -> int:
        """Return hash based on area_id."""
        return hash(self.area_id)

    def __eq__(self, other: object) -> bool:
        """Check equality based on area_id."""
        if not isinstance(other, AreaBridge):
            return False
        return self.area_id == other.area_id
