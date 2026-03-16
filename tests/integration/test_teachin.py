"""Integration test: UTE teach-in auto-response.

Enables teach-in mode on the dongle switch entity, injects a UTE teach-in
packet, and verifies the integration sends a UTE response frame.
"""

import time

from helpers import dongle, packets

TEACHIN_SWITCH_ENTITY = "switch.enocean_custom_teach_in"
NEW_DEVICE_ID = [0xCA, 0xFE, 0xBA, 0xBE]

# UTE RORG
_UTE_RORG = 0xD4


def test_ute_teachin_auto_response(ha_client):
    """With teach-in mode active, a UTE request triggers a UTE response frame."""
    # Enable teach-in mode
    resp = ha_client.post(
        "/api/services/switch/turn_on",
        json={"entity_id": TEACHIN_SWITCH_ENTITY},
    )
    assert resp.status_code == 200
    time.sleep(0.5)

    # Inject UTE teach-in request from a new device
    frame = packets.ute_teach_in_packet(NEW_DEVICE_ID)
    dongle.inject(frame)

    # Integration should respond with a UTE response packet
    response = dongle.read_response(timeout=2.0)

    assert response[0] == 0x55, "Missing ESP3 sync byte in response"
    assert response[6] == _UTE_RORG, (
        f"Expected UTE RORG 0xD4 in response, got 0x{response[6]:02X}"
    )

    # Disable teach-in mode after test
    ha_client.post(
        "/api/services/switch/turn_off",
        json={"entity_id": TEACHIN_SWITCH_ENTITY},
    )
