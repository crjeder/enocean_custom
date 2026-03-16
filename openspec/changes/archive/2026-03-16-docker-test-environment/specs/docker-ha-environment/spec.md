## ADDED Requirements

### Requirement: HA container starts with custom integration mounted
The system SHALL provide a `docker-compose.test.yml` that starts an official Home Assistant container with `enocean_custom` mounted as a custom component and a pre-seeded `configuration.yaml` pointing to the virtual serial device.

#### Scenario: Container starts successfully
- **WHEN** `docker compose -f docker-compose.test.yml up homeassistant` is executed
- **THEN** the HA container reaches a running state and `/api/` returns HTTP 200 within 60 seconds

#### Scenario: Custom integration is loaded
- **WHEN** HA has started and the REST API is reachable
- **THEN** `GET /api/states` returns at least one entity with entity_id prefixed `enocean_custom`

### Requirement: Pre-seeded HA configuration
The system SHALL include a versioned `docker/ha-config/` directory containing `configuration.yaml`, a minimal `auth` file, and `.storage/` bootstrap files so that HA starts without interactive onboarding.

#### Scenario: No interactive onboarding required
- **WHEN** the HA container starts with the pre-seeded config volume
- **THEN** the API token in `docker/ha-config/.env.test` grants authenticated access to `/api/` without any manual setup step

### Requirement: Isolated bridge network
The system SHALL place the `homeassistant` and `test-runner` services on a dedicated Docker bridge network so they can reach each other by service name.

#### Scenario: Test runner reaches HA by hostname
- **WHEN** the test-runner container sends `GET http://homeassistant:8123/api/`
- **THEN** the request succeeds (HTTP 200)
