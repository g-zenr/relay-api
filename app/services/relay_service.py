from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone

from app.core.device import RelayDevice
from app.core.exceptions import InvalidChannelError
from app.models.schemas import DeviceInfo, RelayState, RelayStatus

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("relay.audit")


class RelayService:
    """Thread-safe orchestration layer for relay operations.

    Manages relay state tracking and serializes device access
    via a lock to prevent concurrent HID writes.
    """

    def __init__(self, device: RelayDevice, channels: int):
        self._device = device
        self._channels = channels
        self._lock = threading.Lock()
        self._states: dict[int, RelayState] = {
            ch: RelayState.OFF for ch in range(1, channels + 1)
        }

    def _validate_channel(self, channel: int) -> None:
        if channel < 1 or channel > self._channels:
            raise InvalidChannelError(channel, self._channels)

    def _audit(self, action: str, channel: int | None, state: RelayState) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        target = f"channel={channel}" if channel else "all"
        audit_logger.info("%s | %s | %s → %s", ts, action, target, state.value)

    def set_channel(self, channel: int, state: RelayState) -> RelayStatus:
        self._validate_channel(channel)
        on = state == RelayState.ON
        with self._lock:
            self._device.set_channel(channel, on)
            self._states[channel] = state
            logger.info("Channel %d set to %s", channel, state.value)
        self._audit("set_channel", channel, state)
        return RelayStatus(channel=channel, state=state)

    def get_channel(self, channel: int) -> RelayStatus:
        self._validate_channel(channel)
        return RelayStatus(channel=channel, state=self._states[channel])

    def get_all_channels(self) -> list[RelayStatus]:
        return [
            RelayStatus(channel=ch, state=self._states[ch])
            for ch in range(1, self._channels + 1)
        ]

    def set_all_channels(self, state: RelayState) -> list[RelayStatus]:
        """Set all channels to the same state atomically.

        On partial failure, rolls back successfully-set channels to their
        previous state (best-effort) and re-raises the original exception.
        """
        on = state == RelayState.ON
        with self._lock:
            previous = dict(self._states)
            completed: list[int] = []
            try:
                for ch in range(1, self._channels + 1):
                    self._device.set_channel(ch, on)
                    self._states[ch] = state
                    completed.append(ch)
            except Exception:
                for ch in completed:
                    try:
                        self._device.set_channel(
                            ch, previous[ch] == RelayState.ON
                        )
                    except Exception:
                        logger.exception(
                            "Rollback failed for channel %d", ch
                        )
                    self._states[ch] = previous[ch]
                raise
            logger.info("All channels set to %s", state.value)
        self._audit("set_all_channels", None, state)
        return self.get_all_channels()

    def all_off(self) -> None:
        """Fail-safe: turn all channels OFF."""
        with self._lock:
            for ch in range(1, self._channels + 1):
                try:
                    self._device.set_channel(ch, False)
                except Exception:
                    logger.exception("Fail-safe OFF failed for channel %d", ch)
                self._states[ch] = RelayState.OFF
            logger.info("Fail-safe: all channels OFF")
        self._audit("fail_safe", None, RelayState.OFF)

    @property
    def channel_count(self) -> int:
        return self._channels

    @property
    def is_device_connected(self) -> bool:
        return self._device.is_open

    def get_device_info(self) -> DeviceInfo:
        return DeviceInfo(
            manufacturer=self._device.manufacturer,
            product=self._device.product,
            channels=self._channels,
            connected=self._device.is_open,
        )
