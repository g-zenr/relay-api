from __future__ import annotations

import logging
import threading

import pytest

from app.core.device import MockRelayDevice
from app.core.exceptions import DeviceConnectionError, InvalidChannelError
from app.models.schemas import DeviceInfo, RelayState, RelayStatus
from app.services.relay_service import RelayService


class TestRelayServiceInit:
    def test_all_channels_start_off(self, service: RelayService) -> None:
        statuses = service.get_all_channels()
        assert all(s.state == RelayState.OFF for s in statuses)

    def test_channel_count(self, service: RelayService) -> None:
        assert service.channel_count == 2

    def test_is_device_connected_when_open(self, service: RelayService) -> None:
        assert service.is_device_connected is True

    def test_is_device_connected_when_closed(
        self, service_disconnected: RelayService
    ) -> None:
        assert service_disconnected.is_device_connected is False


class TestSetChannel:
    def test_set_channel_on(
        self, service: RelayService, mock_device: MockRelayDevice
    ) -> None:
        result = service.set_channel(1, RelayState.ON)
        assert result == RelayStatus(channel=1, state=RelayState.ON)
        assert mock_device._states[1] is True

    def test_set_channel_off(
        self, service: RelayService, mock_device: MockRelayDevice
    ) -> None:
        service.set_channel(1, RelayState.ON)
        result = service.set_channel(1, RelayState.OFF)
        assert result.state == RelayState.OFF
        assert mock_device._states[1] is False

    def test_set_channel_updates_state(self, service: RelayService) -> None:
        service.set_channel(2, RelayState.ON)
        status = service.get_channel(2)
        assert status.state == RelayState.ON

    def test_set_channel_invalid_zero(self, service: RelayService) -> None:
        with pytest.raises(InvalidChannelError):
            service.set_channel(0, RelayState.ON)

    def test_set_channel_invalid_too_high(self, service: RelayService) -> None:
        with pytest.raises(InvalidChannelError):
            service.set_channel(3, RelayState.ON)

    def test_set_channel_invalid_negative(self, service: RelayService) -> None:
        with pytest.raises(InvalidChannelError):
            service.set_channel(-1, RelayState.ON)

    def test_set_channel_device_disconnected(
        self, service_disconnected: RelayService
    ) -> None:
        with pytest.raises(DeviceConnectionError):
            service_disconnected.set_channel(1, RelayState.ON)


class TestGetChannel:
    def test_get_channel_default(self, service: RelayService) -> None:
        result = service.get_channel(1)
        assert result == RelayStatus(channel=1, state=RelayState.OFF)

    def test_get_channel_after_set(self, service: RelayService) -> None:
        service.set_channel(1, RelayState.ON)
        result = service.get_channel(1)
        assert result.state == RelayState.ON

    def test_get_channel_invalid(self, service: RelayService) -> None:
        with pytest.raises(InvalidChannelError):
            service.get_channel(99)


class TestGetAllChannels:
    def test_returns_all_channels(self, service: RelayService) -> None:
        result = service.get_all_channels()
        assert len(result) == 2
        assert result[0].channel == 1
        assert result[1].channel == 2

    def test_reflects_mixed_states(self, service: RelayService) -> None:
        service.set_channel(1, RelayState.ON)
        result = service.get_all_channels()
        assert result[0].state == RelayState.ON
        assert result[1].state == RelayState.OFF


class TestSetAllChannels:
    def test_set_all_on(
        self, service: RelayService, mock_device: MockRelayDevice
    ) -> None:
        result = service.set_all_channels(RelayState.ON)
        assert all(s.state == RelayState.ON for s in result)
        assert mock_device._states[1] is True
        assert mock_device._states[2] is True

    def test_set_all_off(
        self, service: RelayService, mock_device: MockRelayDevice
    ) -> None:
        service.set_all_channels(RelayState.ON)
        result = service.set_all_channels(RelayState.OFF)
        assert all(s.state == RelayState.OFF for s in result)
        assert mock_device._states[1] is False
        assert mock_device._states[2] is False

    def test_set_all_device_disconnected(
        self, service_disconnected: RelayService
    ) -> None:
        with pytest.raises(DeviceConnectionError):
            service_disconnected.set_all_channels(RelayState.ON)


class TestSetAllChannelsRollback:
    """Partial failure must roll back successfully-set channels."""

    def test_rolls_back_on_partial_failure(self) -> None:
        device = _FailingMockDevice(fail_on_channel=2, channels=2)
        device.open()
        svc = RelayService(device, channels=2)

        with pytest.raises(DeviceConnectionError):
            svc.set_all_channels(RelayState.ON)

        assert svc.get_channel(1).state == RelayState.OFF
        assert svc.get_channel(2).state == RelayState.OFF

    def test_rollback_restores_previous_state(self) -> None:
        device = _FailingMockDevice(fail_on_channel=2, channels=2)
        device.open()
        svc = RelayService(device, channels=2)

        svc.set_channel(1, RelayState.ON)

        with pytest.raises(DeviceConnectionError):
            svc.set_all_channels(RelayState.OFF)

        assert svc.get_channel(1).state == RelayState.ON

    def test_device_state_matches_after_rollback(self) -> None:
        device = _FailingMockDevice(fail_on_channel=2, channels=2)
        device.open()
        svc = RelayService(device, channels=2)

        with pytest.raises(DeviceConnectionError):
            svc.set_all_channels(RelayState.ON)

        assert device._states[1] is False


class TestAllOff:
    def test_all_off_resets_states(self, service: RelayService) -> None:
        service.set_channel(1, RelayState.ON)
        service.set_channel(2, RelayState.ON)
        service.all_off()
        result = service.get_all_channels()
        assert all(s.state == RelayState.OFF for s in result)

    def test_all_off_sends_commands(
        self, service: RelayService, mock_device: MockRelayDevice
    ) -> None:
        service.set_channel(1, RelayState.ON)
        service.all_off()
        assert mock_device._states[1] is False

    def test_all_off_on_disconnected_still_resets_states(
        self, service_disconnected: RelayService
    ) -> None:
        """Fail-safe must set internal states to OFF even if device raises."""
        service_disconnected.all_off()
        result = service_disconnected.get_all_channels()
        assert all(s.state == RelayState.OFF for s in result)


class TestGetDeviceInfo:
    def test_returns_device_info_connected(self, service: RelayService) -> None:
        info = service.get_device_info()
        assert isinstance(info, DeviceInfo)
        assert info.manufacturer == "MockManufacturer"
        assert info.product == "MockRelay"
        assert info.channels == 2
        assert info.connected is True

    def test_returns_device_info_disconnected(
        self, service_disconnected: RelayService
    ) -> None:
        info = service_disconnected.get_device_info()
        assert info.connected is False
        assert info.manufacturer == "Unknown"


class TestThreadSafety:
    def test_concurrent_set_channel(self, service: RelayService) -> None:
        """Multiple threads setting channels should not corrupt state."""
        errors: list[Exception] = []

        def toggle(channel: int) -> None:
            try:
                for _ in range(50):
                    service.set_channel(channel, RelayState.ON)
                    service.set_channel(channel, RelayState.OFF)
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=toggle, args=(1,))
        t2 = threading.Thread(target=toggle, args=(2,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert errors == []
        result = service.get_all_channels()
        assert all(s.state == RelayState.OFF for s in result)


class TestAuditLogging:
    def test_set_channel_audit(
        self, service: RelayService, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO, logger="relay.audit"):
            service.set_channel(1, RelayState.ON)
        assert "set_channel" in caplog.text
        assert "channel=1" in caplog.text
        assert "on" in caplog.text

    def test_set_all_channels_audit(
        self, service: RelayService, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO, logger="relay.audit"):
            service.set_all_channels(RelayState.OFF)
        assert "set_all_channels" in caplog.text
        assert "all" in caplog.text
        assert "off" in caplog.text

    def test_all_off_audit(
        self, service: RelayService, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO, logger="relay.audit"):
            service.all_off()
        assert "fail_safe" in caplog.text
        assert "off" in caplog.text

    def test_audit_includes_iso_timestamp(
        self, service: RelayService, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO, logger="relay.audit"):
            service.set_channel(1, RelayState.ON)
        # ISO 8601 timestamps contain 'T' between date and time
        assert "T" in caplog.text


# ─── Helpers ───


class _FailingMockDevice(MockRelayDevice):
    """Mock device that raises on a specific channel."""

    def __init__(self, fail_on_channel: int, **kwargs: int):
        super().__init__(**kwargs)
        self._fail_on_channel = fail_on_channel

    def set_channel(self, channel: int, on: bool) -> None:
        if channel == self._fail_on_channel:
            raise DeviceConnectionError(
                f"Simulated failure on channel {channel}"
            )
        super().set_channel(channel, on)
