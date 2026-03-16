# Testing

## Unit tests

The embedded enocean library ships its own test suite that runs directly via Python (no pytest):

```bash
./scripts/test-unit.sh
```

Or individually:

```bash
python custom_components/enocean_custom/enocean/protocol/tests/test_packet.py
python custom_components/enocean_custom/enocean/protocol/tests/test_eep.py
```

---

## Integration tests (Docker)

The integration test suite spins up a real Home Assistant instance inside Docker and exercises the integration end-to-end using a virtual serial dongle.

### Prerequisites

| Requirement | Notes |
|---|---|
| Docker Engine 24+ | Linux containers required |
| Docker Compose v2 | Bundled with Docker Desktop |
| WSL2 (Windows only) | Docker Desktop with "Use WSL 2 based engine" enabled |

### Run locally

```bash
./scripts/test-integration.sh
```

This will:
1. Build the `test-runner` image
2. Start the `serial-bridge` sidecar (socat PTY pair)
3. Start Home Assistant with `enocean_custom` mounted and pre-configured
4. Wait for HA to become healthy (up to 60 s)
5. Run `pytest tests/integration/` inside the test-runner container
6. Print pass/fail and tear down all containers and volumes

Test results are also written to a JUnit XML file inside the `ha-results` Docker volume. To retrieve them after a run:

```bash
docker run --rm \
  -v enocean_custom_ha-results:/results \
  -v "$(pwd)/test-results":/out \
  alpine sh -c "cp /results/test-results.xml /out/"
```

### Environment variables

The test runner reads these variables (set automatically by `docker-compose.test.yml`):

| Variable | Description |
|---|---|
| `HA_URL` | Base URL of the HA instance |
| `HA_WS_URL` | WebSocket URL for HA event subscription |
| `HA_TOKEN` | Long-lived access token |
| `DONGLE_TEST_SIDE` | Path to the test-end PTY inside the test-runner container |

### Virtual serial device

A `socat` sidecar creates a PTY pair:

- `/vserial/ha_end` → symlinked to `/dev/ttyVirtual0` inside the HA container (the dongle device)
- `/vserial/test_end` → used by the test runner to inject/read raw ESP3 frames

The device path `/dev/ttyVirtual0` is fixed and must match `docker/ha-config/configuration.yaml`.

### Adding new tests

1. Add a test file under `tests/integration/`
2. Use the fixtures from `conftest.py` (`ha_client`, `ha_ws`)
3. Use helpers from `tests/integration/helpers/`:
   - `dongle.inject(bytes)` — send an ESP3 frame to HA
   - `dongle.read_response(timeout)` — read a frame HA sends to the dongle
   - `packets.*` — pre-built frame constructors for common EEP types

### CI

The integration tests run automatically on every push and pull request to `main` via `.github/workflows/integration-tests.yml`. Test results are uploaded as a GitHub Actions artifact (`integration-test-results`).
