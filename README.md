# HomeKit Areas

Custom integration for Home Assistant that creates **one independent HomeKit
Bridge per Home Assistant area**, reusing the official HomeKit integration.

```text
Home Assistant
├── Salón       → HomeKit Salón  (port 21070)
├── Cocina      → HomeKit Cocina (port 21071)
└── Dormitorio  → HomeKit Dormitorio (port 21072)
```

Each accessory remains individual and independent in Apple Home.

## Status

In development. Current version: `0.1.0` (skeleton). See
[`docs/homekit-architecture.md`](docs/homekit-architecture.md) for the design.

## Requirements

- Home Assistant `>= 2026.8`
- The official `homekit` integration (bundled with Home Assistant)

## Installation

### HACS

1. Add this repository as a custom repository in HACS (category: Integration).
2. Search for "HomeKit Areas" and install it.
3. Restart Home Assistant.

### Manual

Copy the `custom_components/homekit_areas/` directory into your
`/config/custom_components/` folder and restart Home Assistant.

## Configuration

```text
Settings → Devices & services → Add integration → HomeKit Areas
```

## How it works

HomeKit Areas acts as an **orchestrator**: for each managed area it creates a
`ConfigEntry` of the official `homekit` domain with an entity filter limited
to that area. Pairing, mDNS, HAP and accessory management are handled entirely
by the official HomeKit integration — HomeKit Areas never implements the
HomeKit protocol.

## Ports

HomeKit Areas uses the `21070+` range and never touches existing HomeKit
bridges (typically `21063`/`21064`). Ports are persisted per area and are not
recalculated by area order.

## Compatibility

Tested against Home Assistant `2026.8.x`.

## License

MIT
