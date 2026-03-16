"""Integration test: D2-05-00 roller shutter position reporting.

Injects a VLD position-report packet and verifies the cover entity state
updates to reflect the reported position.
"""

import time

from helpers import dongle, packets

COVER_ENTITY = "cover.test_cover"
# Sender ID must match configuration.yaml
SENDER_ID = [0xDE, 0xAD, 0xBE, 0xEF]


def test_cover_position_update(ha_client, ha_ws):
    """Injecting a D2-05-00 position packet updates the cover entity position."""
    target_position = 42

    frame = packets.bs4_d2_05_00_packet(SENDER_ID, position=target_position)
    dongle.inject(frame)

    ha_ws.wait_for_state(COVER_ENTITY, "open", timeout=5.0)

    resp = ha_client.get(f"/api/states/{COVER_ENTITY}")
    assert resp.status_code == 200
    state = resp.json()
    assert int(state["attributes"].get("current_position", -1)) == target_position


def test_cover_closed_position(ha_client, ha_ws):
    """Position 0 causes the cover entity to report closed."""
    frame = packets.bs4_d2_05_00_packet(SENDER_ID, position=0)
    dongle.inject(frame)

    ha_ws.wait_for_state(COVER_ENTITY, "closed", timeout=5.0)

    resp = ha_client.get(f"/api/states/{COVER_ENTITY}")
    assert resp.status_code == 200
    state = resp.json()
    assert state["state"] == "closed"
