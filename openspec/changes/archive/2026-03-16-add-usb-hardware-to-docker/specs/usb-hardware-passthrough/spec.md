## ADDED Requirements

### Requirement: USB device override file exists
A `docker-compose.usb.yml` file SHALL exist at the repository root and be usable as a Docker Compose override layered on top of `docker-compose.test.yml`.

#### Scenario: Override file is valid compose YAML
- **WHEN** `docker compose -f docker-compose.test.yml -f docker-compose.usb.yml config` is run on a host without a USB device present
- **THEN** the command exits with code 0 and emits valid merged compose YAML

### Requirement: USB device path is configurable via environment variable
The override file SHALL use `${ENOCEAN_DEVICE:-/dev/ttyUSB0}` as the host device path so developers can point to any serial port without editing files.

#### Scenario: Default device path used when env var is unset
- **WHEN** `ENOCEAN_DEVICE` is not set in the shell environment
- **THEN** the merged config references `/dev/ttyUSB0` as the host device

#### Scenario: Custom device path used when env var is set
- **WHEN** `ENOCEAN_DEVICE=/dev/ttyACM0` is exported before `docker compose ... up`
- **THEN** the merged config references `/dev/ttyACM0` as the host device

### Requirement: Home Assistant container receives the USB device
The `homeassistant` service in the override SHALL mount the host USB device into the container under the same path.

#### Scenario: Device node is accessible inside the container
- **WHEN** the compose stack is started with a connected USB dongle on the host
- **THEN** the USB device node is present inside the `homeassistant` container at `${ENOCEAN_DEVICE}`

### Requirement: HA configuration reads dongle path from environment
`docker/ha-config/configuration.yaml` SHALL use the `!env_var` HA YAML tag to read `ENOCEAN_DEVICE` with a default of `/dev/ttyVirtual0`, so the file works in both virtual and hardware modes.

#### Scenario: Virtual mode (no env var set)
- **WHEN** `ENOCEAN_DEVICE` is not set and the virtual compose stack runs
- **THEN** HA loads the integration pointing at `/dev/ttyVirtual0`

#### Scenario: Hardware mode (env var set)
- **WHEN** `ENOCEAN_DEVICE=/dev/ttyUSB0` is set and the USB override stack runs
- **THEN** HA loads the integration pointing at `/dev/ttyUSB0`

### Requirement: Base compose file remains unchanged for CI
The base `docker-compose.test.yml` SHALL require no modification; CI pipelines that run without the override MUST continue to work.

#### Scenario: CI run without override succeeds
- **WHEN** `docker compose -f docker-compose.test.yml up` is run (no USB override)
- **THEN** the virtual serial bridge is used and no errors occur due to missing USB configuration
