#!/bin/sh
# start-virtual-serial.sh
#
# Creates a socat PTY pair for virtual EnOcean dongle testing.
#
# PTY endpoints written to $VSERIAL_DIR:
#   ha_end   → mounted into the HA container as /dev/ttyVirtual0
#   test_end → used by the test runner to inject/read packets
#
# Usage: VSERIAL_DIR=/vserial ./start-virtual-serial.sh

set -e

VSERIAL_DIR="${VSERIAL_DIR:-/vserial}"

echo "Starting virtual serial pair in ${VSERIAL_DIR} ..."

exec socat \
  "PTY,link=${VSERIAL_DIR}/ha_end,rawer,b57600,perm=0666" \
  "PTY,link=${VSERIAL_DIR}/test_end,rawer,b57600,perm=0666"
