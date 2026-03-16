"""Virtual dongle I/O helpers.

Wraps the test-end PTY of the socat pair so tests can inject raw ESP3
frames and read responses without dealing with file descriptors directly.

The PTY path is read from the ``DONGLE_TEST_SIDE`` environment variable
(default: ``/vserial/test_end``).
"""

import os
import select
import time

_DONGLE_PATH = os.environ.get("DONGLE_TEST_SIDE", "/vserial/test_end")
_fd: int | None = None


def _get_fd() -> int:
    """Open the test-end PTY lazily (once per process)."""
    global _fd
    if _fd is None:
        _fd = os.open(_DONGLE_PATH, os.O_RDWR | os.O_NOCTTY)
    return _fd


def inject(packet_bytes: bytes) -> None:
    """Write a raw ESP3 frame to the virtual dongle (HA-side receives it)."""
    fd = _get_fd()
    total = 0
    while total < len(packet_bytes):
        written = os.write(fd, packet_bytes[total:])
        total += written


def read_response(timeout: float = 2.0) -> bytes:
    """Read a raw ESP3 response frame from the virtual dongle.

    Reads available bytes within *timeout* seconds.  Returns all bytes
    received; raises ``TimeoutError`` if nothing arrives.
    """
    fd = _get_fd()
    deadline = time.monotonic() + timeout
    buf = b""

    while time.monotonic() < deadline:
        remaining = deadline - time.monotonic()
        ready, _, _ = select.select([fd], [], [], max(0.0, remaining))
        if ready:
            chunk = os.read(fd, 4096)
            buf += chunk
            # Attempt to detect end of a complete frame (sync byte 0x55 at start)
            if len(buf) >= 6 and buf[0] == 0x55:
                # ESP3 header: sync(1) + data_len(2) + opt_len(1) + type(1) + crc8h(1)
                data_len = (buf[1] << 8) | buf[2]
                opt_len = buf[3]
                expected = 6 + data_len + opt_len + 1  # +1 for CRC8D
                if len(buf) >= expected:
                    return buf[:expected]
        else:
            break

    if not buf:
        raise TimeoutError(
            f"No response from virtual dongle within {timeout}s"
        )
    return buf


def close() -> None:
    """Close the PTY file descriptor (call in test teardown if needed)."""
    global _fd
    if _fd is not None:
        os.close(_fd)
        _fd = None
