## Why

The Docker test environment currently only supports a virtual serial bridge (socat PTY pair), making it impossible to run integration tests against a real EnOcean USB dongle. Developers with physical hardware cannot validate actual device communication without leaving Docker.

## What Changes

- Add USB device passthrough configuration to the `homeassistant` service in `docker-compose.test.yml`
- Add an optional `docker-compose.usb.yml` override file so real hardware can be used without modifying the base compose file
- Document how to discover the dongle's host device path and activate the override

## Capabilities

### New Capabilities

- `usb-hardware-passthrough`: Exposes a host USB serial device (e.g. `/dev/ttyUSB0`) into the Home Assistant container, allowing integration tests to run against real EnOcean hardware instead of the virtual serial bridge

### Modified Capabilities

<!-- No existing spec-level behavior changes -->

## Impact

- `docker-compose.test.yml` — minor: `homeassistant` service may gain a `devices` stanza (or this lives entirely in the override file)
- New file: `docker-compose.usb.yml` — Docker Compose override for hardware mode
- `docker/ha-config/` — may need a second HA config variant or an env-driven dongle path
- Documentation (`README.md` or `docker/README.md`) — instructions for finding and passing through the USB device
- No changes to the integration source code or test logic
