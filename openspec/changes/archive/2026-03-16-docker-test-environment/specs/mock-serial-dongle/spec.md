## ADDED Requirements

### Requirement: Virtual serial PTY pair via socat
The system SHALL create a linked PTY pair using `socat` so that one end acts as the EnOcean dongle device inside the HA container and the other end is writable by the test runner.

#### Scenario: HA integration opens the virtual device
- **WHEN** HA starts with `configuration.yaml` pointing to `/dev/ttyVirtual0`
- **THEN** the `enocean_custom` integration successfully opens the serial port and the dongle entity appears in HA's entity registry

#### Scenario: Test runner injects a packet
- **WHEN** the test runner writes a valid EnOcean radio packet (ESP3 frame) to the write-end of the PTY pair
- **THEN** the HA integration receives the packet and processes it as if it came from a real dongle

### Requirement: Packet capture from HA to test runner
The system SHALL allow the test runner to read packets that HA sends to the dongle (e.g., command frames), so that output assertions can be made.

#### Scenario: Command packet is readable by test runner
- **WHEN** HA sends a command packet to the dongle device
- **THEN** the test runner reads the raw bytes from the write-end of the PTY pair within 2 seconds

### Requirement: Fixed virtual device path
The virtual serial device path inside the HA container SHALL be `/dev/ttyVirtual0`. This path MUST match the value in the pre-seeded `configuration.yaml`.

#### Scenario: Path matches configuration
- **WHEN** `docker-compose.test.yml` is used to start the environment
- **THEN** the device at `/dev/ttyVirtual0` inside the HA container is the same PTY endpoint configured in `configuration.yaml`

### Requirement: Helper library for packet injection
The system SHALL provide a Python helper module (`tests/integration/helpers/dongle.py`) with functions to inject raw ESP3 frames and read response frames, abstracting the PTY file descriptor.

#### Scenario: Inject helper sends a valid packet
- **WHEN** `dongle.inject(packet_bytes)` is called from a test
- **THEN** the bytes appear on the HA-side PTY endpoint without modification
