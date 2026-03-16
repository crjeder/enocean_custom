## 1. Docker Environment Setup

- [x] 1.1 Create `docker/` directory structure: `docker/ha-config/`, `docker/test-runner/`
- [x] 1.2 Write `docker/ha-config/configuration.yaml` that loads `enocean_custom` with dongle path `/dev/ttyVirtual0`
- [x] 1.3 Generate pre-seeded HA auth files and `.storage/` bootstrap (onboarding bypass) and commit to `docker/ha-config/`
- [x] 1.4 Create `docker/ha-config/.env.test` with the long-lived API token for test use
- [x] 1.5 Write `docker/test-runner/Dockerfile` (Python 3.12-slim, installs `pytest`, `httpx`, `websockets`, `socat`)
- [x] 1.6 Write `docker-compose.test.yml` with `homeassistant` and `test-runner` services on a shared bridge network, mounting `custom_components/` and `docker/ha-config/`

## 2. Mock Serial Dongle

- [x] 2.1 Add `socat` PTY-pair startup script `docker/scripts/start-virtual-serial.sh` that creates `/dev/ttyVirtual0` inside the HA container and exposes the other end as a named socket or file path reachable by the test runner
- [x] 2.2 Wire the `socat` sidecar (or entrypoint hook) into `docker-compose.test.yml` so the PTY pair is ready before HA starts
- [x] 2.3 Create `tests/integration/helpers/__init__.py` and `tests/integration/helpers/dongle.py` with `inject(packet_bytes)` and `read_response(timeout)` functions operating on the PTY write-end
- [x] 2.4 Add ESP3 frame builder helpers in `tests/integration/helpers/packets.py` for common packet types (RPS, 1BS, 4BS D2-05-00, UTE)

## 3. HA Healthcheck & Fixtures

- [x] 3.1 Create `tests/integration/conftest.py` with a session-scoped fixture that polls `GET /api/` until HTTP 200 (max 60 s) and raises `TimeoutError` on failure
- [x] 3.2 Add a fixture that provides an authenticated `httpx.Client` using the token from `.env.test`
- [x] 3.3 Add a fixture that provides a connected WebSocket client subscribed to `state_changed` events
- [x] 3.4 Add a per-test fixture that reloads the enocean integration (via `homeassistant.reload_config_entry` service) to achieve test isolation

## 4. Integration Tests

- [x] 4.1 Write `tests/integration/test_cover.py`: inject D2-05-00 position packet → assert `cover.*` entity state matches position
- [x] 4.2 Write `tests/integration/test_binary_sensor.py`: inject D5-00-01 open packet → assert `binary_sensor.*` becomes `on`
- [x] 4.3 Write `tests/integration/test_cover_command.py`: call `cover.set_cover_position` service → assert serial output contains correct D2-05-00 command frame
- [x] 4.4 Write `tests/integration/test_teachin.py`: enable teach-in mode, inject UTE packet → assert UTE response is sent on serial output
- [x] 4.5 Add `pytest.ini` (or `pyproject.toml` section) configuring `testpaths = tests/integration` and `asyncio_mode = auto`

## 5. CI Pipeline

- [x] 5.1 Write `.github/workflows/integration-tests.yml` that triggers on push and PR to `main`, builds Docker images, starts `docker-compose.test.yml`, runs pytest inside the test-runner container
- [x] 5.2 Add Docker layer caching to the workflow using `actions/cache` with the Docker build cache key based on `Dockerfile` and `docker-compose.test.yml` hashes
- [x] 5.3 Configure the workflow to upload `test-results.xml` (pytest `--junitxml`) as a GitHub Actions artifact
- [x] 5.4 Write `scripts/test-integration.sh` and `scripts/test-unit.sh` (replaced Makefile — not a make project)
- [x] 5.5 Update `README` (or add `docs/testing.md`) with instructions for running the integration tests locally and the required prerequisites (Docker, WSL2 on Windows)
