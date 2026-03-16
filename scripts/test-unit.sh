#!/usr/bin/env bash
# Run the embedded enocean library unit tests (no Docker required).
set -euo pipefail

cd "$(dirname "$0")/.."

python custom_components/enocean_custom/enocean/protocol/tests/test_packet.py
python custom_components/enocean_custom/enocean/protocol/tests/test_eep.py
python custom_components/enocean_custom/enocean/protocol/tests/test_teachin.py
python custom_components/enocean_custom/enocean/protocol/tests/test_temperature_sensors.py
python custom_components/enocean_custom/enocean/communicators/tests/test_communicator.py
python custom_components/enocean_custom/enocean/tests/test_utils.py
