## Context

The existing `docker-compose.test.yml` uses a `serial-bridge` service (socat) to create a virtual PTY pair. The `homeassistant` service uses `/dev/ttyVirtual0` (symlinked to `/vserial/ha_end`) as its EnOcean dongle path, and `configuration.yaml` hard-codes `device: /dev/ttyVirtual0`.

Real EnOcean USB300/USB500 dongles appear on the host as `/dev/ttyUSB0` or `/dev/ttyACM0`. Docker Compose supports passing host devices into containers via the `devices` key. The challenge is keeping the base compose file working for CI (no hardware) while enabling hardware mode for local developers.

## Goals / Non-Goals

**Goals:**
- Allow a real USB dongle to be passed through to the `homeassistant` container
- Keep the existing virtual-serial path fully intact (no breakage in CI)
- Minimise changes — one new override file, no restructuring of the base compose

**Non-Goals:**
- Auto-detecting the dongle path on the host
- Supporting Windows host USB passthrough (Linux/macOS only for Docker device passthrough)
- Changing test logic or the test-runner service

## Decisions

### Decision 1: Docker Compose override file (`docker-compose.usb.yml`)

Use `docker compose -f docker-compose.test.yml -f docker-compose.usb.yml up` to layer USB hardware on top of the base config rather than adding conditionals to the base file.

**Why over alternatives:**
- *Env-var toggle inside base file*: Docker Compose does not support conditional `devices` blocks; env vars cannot make a stanza appear/disappear.
- *Separate full compose file*: Would duplicate all service definitions, creating maintenance burden.
- *Override file*: Docker Compose merges override files cleanly; only the delta lives in `docker-compose.usb.yml`. CI continues to run with the base file only.

### Decision 2: Parameterise the device path via `ENOCEAN_DEVICE` env var

The override file maps `${ENOCEAN_DEVICE:-/dev/ttyUSB0}` as the host device, and passes `ENOCEAN_DEVICE` into the `homeassistant` container. `configuration.yaml` is updated to read `device: ${ENOCEAN_DEVICE}`.

**Why:** Developers may have the dongle on `/dev/ttyACM0` or a numbered port. An env var with a sensible default avoids hard-coding.

### Decision 3: Skip the `serial-bridge` healthcheck dependency in hardware mode

In the override file, remove the `depends_on.serial-bridge` condition from `homeassistant` (or override it to `service_started` with `required: false`). The `serial-bridge` service is still defined but is not needed; it will simply exit or idle harmlessly.

**Alternative considered:** Stop `serial-bridge` entirely in the override. This is possible with `profiles:` but adds complexity; letting it idle is simpler.

## Risks / Trade-offs

- **Host device path varies** → Mitigation: document common paths (`/dev/ttyUSB0`, `/dev/ttyACM0`) and the `ls /dev/tty*` discovery command; default env var covers the most common case.
- **Linux kernel `dialout` group** → Mitigation: document that the host user must be in the `dialout` group, or the container runs as `privileged` (acceptable for local dev, not CI).
- **Windows Docker Desktop does not support USB passthrough** → Non-goal; document limitation clearly.
- **`configuration.yaml` env-var substitution** → HA's YAML loader supports `!env_var` tag but not bare `${VAR}` syntax. Mitigation: use `!env_var ENOCEAN_DEVICE /dev/ttyVirtual0` so the file works with or without the env var set.

## Migration Plan

1. Add `docker-compose.usb.yml` (new file, no existing files changed initially).
2. Update `docker/ha-config/configuration.yaml` to use `!env_var ENOCEAN_DEVICE /dev/ttyVirtual0` — this is backward-compatible (default keeps virtual path).
3. Update `docker/scripts/` with a helper script or update docs.
4. No rollback needed — changes are additive; removing the override file reverts to virtual mode.

## Open Questions

- Should `docker-compose.usb.yml` also override `DONGLE_TEST_SIDE` in the `test-runner` to point to the real device (not applicable for real hardware) or skip dongle-simulation entirely? Likely the test-runner's serial simulation is simply not used when real hardware is present.
