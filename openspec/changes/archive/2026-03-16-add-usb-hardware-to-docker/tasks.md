## 1. Update HA Configuration

- [x] 1.1 In `docker/ha-config/configuration.yaml`, replace `device: /dev/ttyVirtual0` with `device: !env_var ENOCEAN_DEVICE /dev/ttyVirtual0`

## 2. Create Docker Compose Override

- [x] 2.1 Create `docker-compose.usb.yml` at the repository root with a `homeassistant` service block that adds `devices: ["${ENOCEAN_DEVICE:-/dev/ttyUSB0}:${ENOCEAN_DEVICE:-/dev/ttyUSB0}"]` and sets the `ENOCEAN_DEVICE` environment variable
- [x] 2.2 In the same override, override `homeassistant.depends_on.serial-bridge` to `required: false` (or remove the dependency) so the virtual bridge is not required in hardware mode

## 3. Verify Compose Validity

- [x] 3.1 Run `docker compose -f docker-compose.test.yml config` and confirm it is valid (virtual mode, no changes)
- [x] 3.2 Run `docker compose -f docker-compose.test.yml -f docker-compose.usb.yml config` and confirm the merged YAML is valid and contains the `devices` stanza

## 4. Documentation

- [x] 4.1 Add a "Hardware mode" section to `README.md` (or create `docker/README.md`) documenting: how to find the dongle path (`ls /dev/ttyUSB* /dev/ttyACM*`), the `dialout` group requirement on Linux, and the `docker compose ... -f docker-compose.usb.yml up` invocation
- [x] 4.2 Note Windows USB passthrough limitation (not supported by Docker Desktop) in the same documentation section
