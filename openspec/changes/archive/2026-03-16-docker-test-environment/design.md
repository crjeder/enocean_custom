## Context

`enocean_custom` is a Home Assistant custom integration. Its only automated tests today are the embedded enocean library's unit tests (run directly via Python). There are no tests that verify the integration behaves correctly inside a running HA instance. This gap means regressions can be introduced silently when HA updates its internals or when the integration's entity/platform code changes.

The integration communicates with a physical USB dongle via a serial port. Tests must work without real hardware, so serial communication must be virtualized.

## Goals / Non-Goals

**Goals:**
- Spin up a real, unmodified HA instance inside Docker with `enocean_custom` mounted as a custom component
- Inject synthetic EnOcean radio packets via a mock serial dongle
- Verify entity states and service calls through HA's REST/WebSocket API
- Run the full suite in CI (GitHub Actions) without human intervention
- Allow developers to run the suite locally with a single command

**Non-Goals:**
- Testing every EEP profile exhaustively (covered by existing unit tests)
- Hardware-in-the-loop testing with a real USB dongle
- Performance/load testing of the HA instance
- Testing other HA integrations or HA core functionality

## Decisions

### D1: Docker Compose orchestration

**Decision**: Use `docker-compose.test.yml` with two services — `homeassistant` and `test-runner` — on a shared bridge network.

**Rationale**: Keeps HA isolated in its official image (`ghcr.io/home-assistant/home-assistant:stable`). The test runner only needs to reach HA's HTTP API and the virtual serial device; it does not need to run inside the HA container.

**Alternative considered**: Single container with HA + tests. Rejected because it requires patching the HA image and complicates upgrades.

### D2: Virtual serial port via `socat`

**Decision**: Use `socat` in a sidecar (or within the test-runner container) to create a linked PTY pair. One end is given to the HA container (via a volume bind or `--device`); the test runner writes raw EnOcean packets to the other end.

**Rationale**: `socat` is the standard tool for virtual serial on Linux; it is available in Alpine/Debian images. A PTY pair behaves identically to a real serial port from the integrations's perspective.

**Alternative considered**: Mock at the Python `serial.Serial` level using `unittest.mock`. Rejected because it requires patching the integration's source, which is fragile and does not exercise the actual serial read path.

### D3: Test framework — pytest + `httpx`/`websockets`

**Decision**: Use `pytest` with `httpx` (sync) for REST calls and `websockets` for the HA WebSocket API.

**Rationale**: `pytest` is the standard Python test runner; `httpx` is lightweight and has no HA-specific coupling. The HA WebSocket API allows subscribing to state-change events, enabling event-driven assertions instead of polling.

**Alternative considered**: `hass-client` library. Rejected because it adds an extra dependency that may lag HA API changes.

### D4: HA configuration pre-seeding

**Decision**: Mount a minimal `configuration.yaml` and `custom_components/` directory into the HA container via Docker volumes. The config declares the EnOcean dongle pointing to the virtual serial device path.

**Rationale**: Avoids HA's interactive onboarding flow. A pre-seeded `auth` and `.storage/` directory (generated once and committed) ensures the API is reachable immediately.

**Alternative considered**: Use HA's `--skip-pip` flag and configure via API. Rejected because the onboarding API is complex and not stable across HA versions.

### D5: Healthcheck before tests

**Decision**: The test runner waits for HA's `/api/` endpoint to return HTTP 200 (polled with retries) before running tests.

**Rationale**: HA can take 10–30 s to start. A simple HTTP healthcheck is more reliable than a fixed `sleep`.

## Risks / Trade-offs

- **HA version drift** → Pin `ghcr.io/home-assistant/home-assistant:stable` and add a Dependabot / Renovate rule to track updates. Run tests on each pin bump.
- **PTY path instability** → The virtual serial device path inside the HA container must match `configuration.yaml`. Use a fixed, agreed-upon path (e.g., `/dev/ttyVirtual0`) and document it.
- **CI runner resource limits** → GitHub Actions free tier has 2 vCPU / 7 GB RAM. HA + Docker is heavy. Mitigate by using HA's `--skip-pip` startup flag and caching the Docker image layer.
- **Flaky timing** → Serial packet injection timing can cause race conditions. Mitigate by subscribing to HA state-change events via WebSocket and waiting for explicit state transitions instead of fixed delays.
- **Windows development** → `socat` and PTYs are Linux-only. Local development on Windows requires WSL2 or Docker Desktop with Linux containers, which is standard.

## Migration Plan

1. Add new files (`docker/`, `tests/integration/`, CI workflow) — no changes to existing code.
2. Generate and commit the pre-seeded HA config directory (`docker/ha-config/`) — one-time setup step documented in `README`.
3. Enable the CI job in GitHub Actions — starts running on the next push.
4. Rollback: disable or delete the CI workflow file; the integration itself is unaffected.

## Open Questions

- Should the test suite also run the existing enocean unit tests (currently run directly via Python), or keep them separate jobs?
- Should we pin to `stable` or a specific HA version tag to avoid unexpected breakage from HA releases?
