"""Integration test: D5-00-01 contact sensor state reporting."""

from helpers import dongle, packets

SENSOR_ENTITY = "binary_sensor.test_contact"
SENDER_ID = [0xDE, 0xAD, 0xBE, 0x01]


def test_contact_open(ha_ws):
    """Injecting a D5 open packet sets the binary_sensor to 'on'."""
    dongle.inject(packets.bs1_packet(SENDER_ID, contact_open=True))
    ha_ws.wait_for_state(SENSOR_ENTITY, "on", timeout=5.0)


def test_contact_closed(ha_ws):
    """Injecting a D5 closed packet sets the binary_sensor to 'off'."""
    dongle.inject(packets.bs1_packet(SENDER_ID, contact_open=False))
    ha_ws.wait_for_state(SENSOR_ENTITY, "off", timeout=5.0)
