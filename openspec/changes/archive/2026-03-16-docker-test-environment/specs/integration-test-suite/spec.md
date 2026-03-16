## ADDED Requirements

### Requirement: Pytest-based test runner
The system SHALL provide a `tests/integration/` directory with `pytest` tests that use HA's REST and WebSocket APIs to assert integration behaviour.

#### Scenario: Test suite runs without errors on a clean environment
- **WHEN** `pytest tests/integration/` is executed inside the test-runner container after HA is healthy
- **THEN** all tests pass and the exit code is 0

### Requirement: Entity state assertions
The system SHALL include tests that verify entity states change correctly after synthetic EnOcean packets are injected.

#### Scenario: Cover entity responds to roller-shutter packet
- **WHEN** a D2-05-00 position packet is injected via the mock serial dongle
- **THEN** the corresponding `cover.*` entity state in HA changes to match the position value within 5 seconds

#### Scenario: Binary sensor entity responds to 1BS packet
- **WHEN** a D5-00-01 contact packet (open) is injected
- **THEN** the corresponding `binary_sensor.*` entity state becomes `on` within 5 seconds

### Requirement: Service call testing
The system SHALL include tests that call HA services (e.g., `cover.set_cover_position`) and verify the resulting serial output.

#### Scenario: Cover set_position sends serial packet
- **WHEN** `cover.set_cover_position` is called with `position: 50` for a configured cover entity
- **THEN** the mock serial dongle receives a correctly formed D2-05-00 command packet within 2 seconds

### Requirement: Teach-in flow testing
The system SHALL include a test that simulates a UTE teach-in exchange and verifies the dongle responds with an acknowledgement packet.

#### Scenario: UTE teach-in auto-response
- **WHEN** a UTE teach-in packet is injected while `teach_in` mode is enabled on the dongle entity
- **THEN** the mock serial dongle receives a UTE response packet within 2 seconds

### Requirement: Test isolation between test cases
Each test case SHALL start from a known state. Tests MUST NOT depend on execution order.

#### Scenario: State is reset between tests
- **WHEN** a test fixture sets up a specific entity state
- **THEN** subsequent tests do not observe that state unless they set it themselves
