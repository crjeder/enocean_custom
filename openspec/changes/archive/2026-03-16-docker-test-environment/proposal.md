## Why

The `enocean_custom` integration currently has no automated integration tests against a real Home Assistant instance, making it difficult to verify compatibility after HA updates or code changes. A Docker-based test environment will enable fully automated, reproducible tests against a clean HA installation in CI/CD pipelines.

## What Changes

- Add `Dockerfile` and `docker-compose.yml` to spin up a clean Home Assistant instance with the integration pre-loaded
- Add a test runner container that executes integration tests against the HA instance
- Add integration test suite covering device setup, entity state, and dongle communication (mocked serial)
- Add GitHub Actions workflow step to run the Docker-based test suite on push/PR
- Add `Makefile` targets (or shell scripts) for local test execution

## Capabilities

### New Capabilities

- `docker-ha-environment`: Docker Compose setup that launches a clean HA instance with `enocean_custom` mounted and pre-configured via `configuration.yaml`
- `integration-test-suite`: Pytest-based integration tests that interact with HA's REST/WebSocket API to verify entity states, service calls, and teach-in flows
- `mock-serial-dongle`: A virtual serial port / mock EnOcean dongle that injects synthetic radio packets into the running HA instance for deterministic testing
- `ci-test-pipeline`: GitHub Actions job that builds and runs the Docker test environment on every push and pull request

### Modified Capabilities

<!-- No existing specs are affected -->

## Impact

- **New files**: `tests/integration/`, `docker/`, `docker-compose.test.yml`, `.github/workflows/integration-tests.yml`, `Makefile`
- **Dependencies**: Docker, `pytest`, `pytest-asyncio`, `homeassistant` Python package (for test client helpers), `socat` or `pty` for virtual serial
- **CI**: Adds a new GitHub Actions job; existing `hassfest` job is unchanged
- **Runtime**: No changes to the integration's production code
