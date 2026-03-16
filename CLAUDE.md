# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration for EnOcean wireless devices (`enocean_custom`). It extends the official HA EnOcean integration with enhanced cover (roller shutter) support and universal teach-in capabilities.

- **Domain**: `enocean_custom`
- **Supported platforms**: cover, binary_sensor, sensor, light, switch
- **IoT class**: Local Push (direct USB dongle communication)

## Running Tests

The embedded enocean library has its own tests using a custom `@timing` decorator (not pytest). Run them directly:

```bash
python custom_components/enocean_custom/enocean/protocol/tests/test_packet.py
python custom_components/enocean_custom/enocean/protocol/tests/test_eep.py
python custom_components/enocean_custom/enocean/protocol/tests/test_teachin.py
python custom_components/enocean_custom/enocean/protocol/tests/test_temperature_sensors.py
python custom_components/enocean_custom/enocean/communicators/tests/test_communicator.py
python custom_components/enocean_custom/enocean/tests/test_utils.py
```

## CI/CD

GitHub Actions runs `home-assistant/actions/hassfest@master` on push/PR to validate `manifest.json` and integration structure.

## Architecture

### Layered Structure

```
HA Platform Layer (cover, switch, sensor, binary_sensor, light)
    ↓
EnOceanEntity base class (dispatcher signals, unique IDs)
    ↓
EnOceanDongle (packet routing, teach-in, base_id management)
    ↓
SerialCommunicator / TCPCommunicator (thread-based I/O at 57600 baud)
    ↓
Protocol Library: Packet / EEP parsing (custom_components/enocean_custom/enocean/)
```

### Key Design Patterns

**Publisher-Subscriber via HA Dispatcher**
- `SIGNAL_RECEIVE_MESSAGE`: Dongle broadcasts received `RadioPacket` to all entities
- `SIGNAL_SEND_MESSAGE`: Entities send commands to dongle
- Defined in `const.py`

**Device Identity**
- Each device has a `dev_id` (4-byte list, e.g. `[0x00, 0x01, 0x02, 0x03]`)
- Unique entity ID: `enocean_<HEX_NO_COLONS>_<channel>`

**EEP (EnOcean Equipment Profile) System**
- RORG byte identifies packet type: `0xA5`=4BS, `0xD2`=VLD, `0xF6`=RPS, `0xD5`=1BS, `0xD4`=UTE
- `packet.select_eep(func, type)` then `packet.parse_eep()` extracts values
- Key device profiles: D2-05-00 (roller shutters), A5-12-01 (power), A5-04 (temp+humidity), F6-02 (wall switches)

**Teach-In**
- `EnOceanDongle` has `teach_in` property toggled via `EnOceanDongleTeachInSwitch`
- UTE packets (`UTETeachInPacket`) are auto-responded to with the dongle's `base_id`

### Embedded Library

The `enocean/` subdirectory is a bundled copy of the kipe/enocean library (rather than an installed package). Modifications to protocol handling go here. The `manifest.json` also declares `enocean>=0.50` as an external dependency — the bundled copy takes precedence at runtime.

### Configuration

Devices are configured via YAML (no auto-discovery). The `config_flow.py` handles dongle path detection and validation for the UI-based setup. Legacy YAML config is imported in `__init__.py:async_setup()`.
