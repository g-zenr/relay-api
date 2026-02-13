from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone

from app.core.device import RelayDevice
from app.core.exceptions import InvalidChannelError
from app.models.schemas import (
    BurnTestMode,
    BurnTestStatus,
    DeviceInfo,
    RelayState,
    RelayStatus,
)

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("relay.audit")


class RelayService:
    """Thread-safe orchestration layer for relay operations.

    Manages relay state tracking and serializes device access
    via a lock to prevent concurrent HID writes.
    """

    def __init__(
        self, device: RelayDevice, channels: int, pulse_ms: int = 0,
    ):
        self._device = device
        self._channels = channels
        self._pulse_ms = pulse_ms
        self._lock = threading.Lock()
        self._states: dict[int, RelayState] = {
            ch: RelayState.OFF for ch in range(1, channels + 1)
        }
        self._pulse_timers: dict[int, threading.Timer] = {}
        self._burn_running = False
        self._burn_stop = threading.Event()
        self._burn_cycles_completed = 0
        self._burn_cycles_target = 0
        self._burn_errors = 0
        self._burn_mode = BurnTestMode.ALL
        self._burn_thread: threading.Thread | None = None

    def _validate_channel(self, channel: int) -> None:
        if channel < 1 or channel > self._channels:
            raise InvalidChannelError(channel, self._channels)

    def _audit(self, action: str, channel: int | None, state: RelayState) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        target = f"channel={channel}" if channel else "all"
        audit_logger.info("%s | %s | %s → %s", ts, action, target, state.value)

    def _cancel_pulse_timer(self, channel: int) -> None:
        """Cancel any pending pulse auto-off timer for a channel."""
        timer = self._pulse_timers.pop(channel, None)
        if timer is not None:
            timer.cancel()

    def _pulse_off(self, channel: int) -> None:
        """Timer callback: turn a channel OFF after a pulse delay."""
        with self._lock:
            try:
                self._device.set_channel(channel, False)
                self._states[channel] = RelayState.OFF
                logger.info("Channel %d pulse OFF (auto)", channel)
            except Exception:
                logger.exception("Pulse auto-off failed for channel %d", channel)
            finally:
                self._pulse_timers.pop(channel, None)
        self._audit("pulse_off", channel, RelayState.OFF)

    def set_channel(self, channel: int, state: RelayState) -> RelayStatus:
        self._validate_channel(channel)
        on = state == RelayState.ON
        self._cancel_pulse_timer(channel)
        with self._lock:
            self._device.set_channel(channel, on)
            self._states[channel] = state
            logger.info("Channel %d set to %s", channel, state.value)
        self._audit("set_channel", channel, state)
        if on and self._pulse_ms > 0:
            timer = threading.Timer(
                self._pulse_ms / 1000.0, self._pulse_off, args=(channel,),
            )
            timer.daemon = True
            self._pulse_timers[channel] = timer
            timer.start()
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

    # --- Burn test ---

    def start_burn_test(
        self, cycles: int, delay_ms: int, mode: BurnTestMode = BurnTestMode.ALL,
    ) -> BurnTestStatus:
        """Start a background burn test that cycles relays."""
        if self._burn_running:
            return self.get_burn_test_status()

        self._burn_stop.clear()
        self._burn_cycles_completed = 0
        self._burn_cycles_target = cycles
        self._burn_errors = 0
        self._burn_mode = mode
        self._burn_running = True

        self._burn_thread = threading.Thread(
            target=self._burn_test_loop,
            args=(cycles, delay_ms / 1000.0, mode),
            daemon=True,
        )
        self._burn_thread.start()
        logger.info(
            "Burn test started: mode=%s, cycles=%s, delay=%dms",
            mode.value,
            cycles if cycles > 0 else "indefinite",
            delay_ms,
        )
        self._audit("burn_test_start", None, RelayState.OFF)
        return self.get_burn_test_status()

    def stop_burn_test(self) -> BurnTestStatus:
        """Stop a running burn test and turn all relays OFF."""
        if not self._burn_running:
            return self.get_burn_test_status()

        self._burn_stop.set()
        if self._burn_thread and self._burn_thread.is_alive():
            self._burn_thread.join(timeout=5.0)

        self.all_off()
        logger.info(
            "Burn test stopped after %d cycles", self._burn_cycles_completed
        )
        self._audit("burn_test_stop", None, RelayState.OFF)
        return self.get_burn_test_status()

    def get_burn_test_status(self) -> BurnTestStatus:
        """Get current burn test status."""
        return BurnTestStatus(
            running=self._burn_running,
            cycles_completed=self._burn_cycles_completed,
            cycles_target=self._burn_cycles_target,
            errors=self._burn_errors,
            mode=self._burn_mode,
        )

    def _burn_test_loop(
        self, cycles: int, delay_s: float, mode: BurnTestMode = BurnTestMode.ALL,
    ) -> None:
        """Background loop that toggles relays based on mode."""
        try:
            if mode == BurnTestMode.ALTERNATE:
                self._burn_loop_alternate(cycles, delay_s)
            else:
                self._burn_loop_all(cycles, delay_s)
        finally:
            self._burn_running = False
            logger.info(
                "Burn test finished: mode=%s, %d cycles, %d errors",
                mode.value,
                self._burn_cycles_completed,
                self._burn_errors,
            )

    def _burn_loop_all(self, cycles: int, delay_s: float) -> None:
        """All channels ON together, then all OFF together."""
        cycle = 0
        while not self._burn_stop.is_set():
            if cycles > 0 and cycle >= cycles:
                break

            # ON phase
            for ch in range(1, self._channels + 1):
                if self._burn_stop.is_set():
                    return
                try:
                    self.set_channel(ch, RelayState.ON)
                except Exception:
                    self._burn_errors += 1
                    logger.exception("Burn test error on channel %d ON", ch)

            if self._burn_stop.wait(delay_s):
                return

            # OFF phase
            for ch in range(1, self._channels + 1):
                if self._burn_stop.is_set():
                    return
                try:
                    self.set_channel(ch, RelayState.OFF)
                except Exception:
                    self._burn_errors += 1
                    logger.exception("Burn test error on channel %d OFF", ch)

            if self._burn_stop.wait(delay_s):
                return

            cycle += 1
            self._burn_cycles_completed = cycle

    def _burn_loop_alternate(self, cycles: int, delay_s: float) -> None:
        """Relay 1 ON / Relay 2 OFF, then swap. Alternating switch test."""
        cycle = 0
        while not self._burn_stop.is_set():
            if cycles > 0 and cycle >= cycles:
                break

            # Phase A: relay 1 ON, relay 2 OFF
            try:
                self.set_channel(1, RelayState.ON)
            except Exception:
                self._burn_errors += 1
                logger.exception("Burn test alternate error: ch1 ON")
            try:
                self.set_channel(2, RelayState.OFF)
            except Exception:
                self._burn_errors += 1
                logger.exception("Burn test alternate error: ch2 OFF")

            if self._burn_stop.wait(delay_s):
                return

            # Phase B: relay 1 OFF, relay 2 ON
            try:
                self.set_channel(1, RelayState.OFF)
            except Exception:
                self._burn_errors += 1
                logger.exception("Burn test alternate error: ch1 OFF")
            try:
                self.set_channel(2, RelayState.ON)
            except Exception:
                self._burn_errors += 1
                logger.exception("Burn test alternate error: ch2 ON")

            if self._burn_stop.wait(delay_s):
                return

            cycle += 1
            self._burn_cycles_completed = cycle
