"""Pytest fixtures for integration tests against a running Home Assistant instance."""

import asyncio
import json
import os
import time

import httpx
import pytest
import websockets

# ── Configuration ────────────────────────────────────────────────────────────

HA_URL = os.environ.get("HA_URL", "http://homeassistant:8123")
HA_TOKEN = os.environ.get("HA_TOKEN", "")
# HA_WS_URL must be set explicitly via environment (see docker-compose.test.yml).
# Use wss:// when running against a TLS-enabled instance.
HA_WS_URL = os.environ["HA_WS_URL"]

ENOCEAN_DOMAIN = "enocean_custom"
HA_STARTUP_TIMEOUT = 60  # seconds


# ── Session-scoped: wait for HA to be ready ──────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def wait_for_ha():
    """Poll GET /api/ until HA is up (max STARTUP_TIMEOUT seconds)."""
    deadline = time.monotonic() + HA_STARTUP_TIMEOUT
    last_exc: Exception | None = None
    while time.monotonic() < deadline:
        try:
            resp = httpx.get(
                f"{HA_URL}/api/",
                headers={"Authorization": f"Bearer {HA_TOKEN}"},
                timeout=5,
            )
            if resp.status_code == 200:
                return
        except Exception as exc:
            last_exc = exc
        time.sleep(2)
    raise TimeoutError(
        f"Home Assistant did not become ready within {HA_STARTUP_TIMEOUT}s. "
        f"Last error: {last_exc}"
    )


# ── Authenticated HTTP client ─────────────────────────────────────────────────

@pytest.fixture
def ha_client(wait_for_ha):
    """An authenticated httpx.Client pointed at the HA REST API."""
    with httpx.Client(
        base_url=HA_URL,
        headers={"Authorization": f"Bearer {HA_TOKEN}"},
        timeout=10,
    ) as client:
        yield client


# ── WebSocket client with state_changed subscription ─────────────────────────

@pytest.fixture
def ha_ws(wait_for_ha):
    """Synchronous wrapper around an authenticated HA WebSocket connection.

    Subscribes to ``state_changed`` events.  Use ``ha_ws.wait_for_state``
    to block until an entity reaches the desired state.
    """

    class _WsClient:
        def __init__(self):
            self._loop = asyncio.new_event_loop()
            self._ws = None
            self._msg_id = 1
            self._loop.run_until_complete(self._connect())

        async def _connect(self):
            self._ws = await websockets.connect(HA_WS_URL)
            # Receive auth_required
            await self._ws.recv()
            # Send auth
            await self._ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
            auth_ok = json.loads(await self._ws.recv())
            assert auth_ok["type"] == "auth_ok", f"Auth failed: {auth_ok}"
            # Subscribe to state_changed
            sub_id = self._msg_id
            self._msg_id += 1
            await self._ws.send(json.dumps({
                "id": sub_id,
                "type": "subscribe_events",
                "event_type": "state_changed",
            }))
            result = json.loads(await self._ws.recv())
            assert result.get("success"), f"Subscribe failed: {result}"

        def wait_for_state(self, entity_id: str, expected_state: str, timeout: float = 5.0) -> str:
            """Block until entity_id reaches expected_state; return the new state string."""
            return self._loop.run_until_complete(
                self._wait_for_state_async(entity_id, expected_state, timeout)
            )

        async def _wait_for_state_async(self, entity_id: str, expected_state: str, timeout: float) -> str:
            deadline = asyncio.get_event_loop().time() + timeout
            while True:
                remaining = deadline - asyncio.get_event_loop().time()
                if remaining <= 0:
                    raise TimeoutError(
                        f"Entity {entity_id!r} did not reach state {expected_state!r} "
                        f"within {timeout}s"
                    )
                try:
                    raw = await asyncio.wait_for(self._ws.recv(), timeout=remaining)
                except asyncio.TimeoutError:
                    raise TimeoutError(
                        f"Entity {entity_id!r} did not reach state {expected_state!r} "
                        f"within {timeout}s"
                    )
                msg = json.loads(raw)
                if msg.get("type") != "event":
                    continue
                event_data = msg.get("event", {}).get("data", {})
                if event_data.get("entity_id") == entity_id:
                    new_state = event_data.get("new_state", {}).get("state")
                    if new_state == expected_state:
                        return new_state

        def close(self):
            self._loop.run_until_complete(self._ws.close())
            self._loop.close()

    client = _WsClient()
    yield client
    client.close()


# ── Per-test: reload the enocean integration for isolation ────────────────────

@pytest.fixture(autouse=True)
def reload_enocean_integration(ha_client):
    """Reload the enocean_custom config entry before each test for isolation."""
    # Find the config entry ID for enocean_custom
    resp = ha_client.get("/api/config/config_entries/entry")
    if resp.status_code == 200:
        entries = resp.json()
        for entry in entries:
            if entry.get("domain") == ENOCEAN_DOMAIN:
                entry_id = entry["entry_id"]
                ha_client.post(
                    "/api/config/config_entries/entry/reload",
                    json={"entry_id": entry_id},
                )
                # Give HA a moment to finish reloading
                time.sleep(2)
                break
    yield
