"""Integration test: cover service call produces correct serial output.

Calls cover.set_cover_position and verifies the integration writes a
D2-05-00 command frame back through the virtual dongle.
"""

from helpers import dongle, packets

COVER_ENTITY = "cover.test_cover"

# D2-05-00 command 0x01 = Go To Position
_D2_RORG = 0xD2
_CMD_GOTO = 0x01


def test_set_cover_position_sends_serial_packet(ha_client):
    """Calling cover.set_cover_position emits a D2-05-00 goto-position frame."""
    resp = ha_client.post(
        "/api/services/cover/set_cover_position",
        json={"entity_id": COVER_ENTITY, "position": 50},
    )
    assert resp.status_code == 200

    raw = dongle.read_response(timeout=2.0)

    # Minimal validation: sync byte present and RORG is D2
    assert raw[0] == 0x55, "Missing ESP3 sync byte"
    # Data starts at offset 6; first data byte is RORG
    assert raw[6] == _D2_RORG, f"Expected RORG 0xD2, got 0x{raw[6]:02X}"
    # Second data byte: upper nibble = command (0x01 = goto position)
    cmd = (raw[7] >> 4) & 0x0F
    assert cmd == _CMD_GOTO, f"Expected CMD 0x01, got 0x{cmd:01X}"
    # Third data byte: position value
    assert raw[8] == 50, f"Expected position 50, got {raw[8]}"
