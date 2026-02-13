from __future__ import annotations

import logging
from typing import Protocol, runtime_checkable

import hid

from app.core.exceptions import DeviceConnectionError, DeviceNotFoundError

logger = logging.getLogger(__name__)


@runtime_checkable
class RelayDevice(Protocol):
    """Abstract interface for a USB relay device.

    Implementations must support open/close lifecycle and
    sending relay commands by channel.
    """

    def open(self) -> None: ...
    def close(self) -> None: ...
    def set_channel(self, channel: int, on: bool) -> None: ...

    @property
    def is_open(self) -> bool: ...
    @property
    def manufacturer(self) -> str: ...
    @property
    def product(self) -> str: ...


# --- DCT Tech HID implementation ---

_COMMAND_ON = 0xFF
_COMMAND_OFF = 0xFD


class HIDRelayDevice:
    """Concrete HID implementation for DCT Tech USB relay modules."""

    def __init__(self, vendor_id: int, product_id: int):
        self._vendor_id = vendor_id
        self._product_id = product_id
        self._device: hid.device | None = None
        self._is_open = False

    def open(self) -> None:
        if self._is_open:
            return
        self._device = hid.device()
        try:
            self._device.open(self._vendor_id, self._product_id)
            self._is_open = True
            logger.info(
                "Device opened: %s - %s", self.manufacturer, self.product
            )
        except IOError as exc:
            self._device = None
            raise DeviceNotFoundError(self._vendor_id, self._product_id) from exc

    def close(self) -> None:
        if self._device and self._is_open:
            self._device.close()
            self._is_open = False
            self._device = None
            logger.info("Device closed")

    def set_channel(self, channel: int, on: bool) -> None:
        if not self._is_open or not self._device:
            raise DeviceConnectionError("Device is not open")
        state = _COMMAND_ON if on else _COMMAND_OFF
        cmd = [0x00, state, channel, 0, 0, 0, 0, 0, 0]
        try:
            self._device.send_feature_report(cmd)
        except IOError as exc:
            raise DeviceConnectionError(
                f"Failed to set channel {channel}: {exc}"
            ) from exc

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def manufacturer(self) -> str:
        if self._device and self._is_open:
            return self._device.get_manufacturer_string() or "Unknown"
        return "Unknown"

    @property
    def product(self) -> str:
        if self._device and self._is_open:
            return self._device.get_product_string() or "Unknown"
        return "Unknown"


# --- In-memory mock implementation ---


class MockRelayDevice:
    """In-memory mock that simulates a relay device without hardware.

    Useful for development, testing, and demos.
    Channel states are tracked in a dict and logged to console.
    """

    def __init__(self, channels: int = 2):
        self._channels = channels
        self._is_open = False
        self._states: dict[int, bool] = {}

    def open(self) -> None:
        self._is_open = True
        self._states = {ch: False for ch in range(1, self._channels + 1)}
        logger.info("MockRelayDevice opened (%d channels)", self._channels)

    def close(self) -> None:
        self._is_open = False
        self._states.clear()
        logger.info("MockRelayDevice closed")

    def set_channel(self, channel: int, on: bool) -> None:
        if not self._is_open:
            raise DeviceConnectionError("Mock device is not open")
        self._states[channel] = on
        state_str = "ON" if on else "OFF"
        logger.info("[MOCK] Channel %d → %s", channel, state_str)

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def manufacturer(self) -> str:
        return "MockManufacturer" if self._is_open else "Unknown"

    @property
    def product(self) -> str:
        return "MockRelay" if self._is_open else "Unknown"
