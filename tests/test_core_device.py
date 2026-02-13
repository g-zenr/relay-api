import pytest

from app.core.device import HIDRelayDevice, MockRelayDevice, RelayDevice
from app.core.exceptions import DeviceConnectionError, DeviceNotFoundError


class TestRelayDeviceProtocol:
    def test_mock_device_satisfies_protocol(self):
        device = MockRelayDevice()
        assert isinstance(device, RelayDevice)

    def test_hid_device_satisfies_protocol(self):
        device = HIDRelayDevice(vendor_id=0x16C0, product_id=0x05DF)
        assert isinstance(device, RelayDevice)

    def test_protocol_requires_open(self):
        assert hasattr(RelayDevice, "open")

    def test_protocol_requires_close(self):
        assert hasattr(RelayDevice, "close")

    def test_protocol_requires_set_channel(self):
        assert hasattr(RelayDevice, "set_channel")

    def test_protocol_requires_is_open(self):
        assert hasattr(RelayDevice, "is_open")

    def test_protocol_requires_manufacturer(self):
        assert hasattr(RelayDevice, "manufacturer")

    def test_protocol_requires_product(self):
        assert hasattr(RelayDevice, "product")


class TestHIDRelayDeviceInit:
    def test_starts_closed(self):
        device = HIDRelayDevice(vendor_id=0x16C0, product_id=0x05DF)
        assert device.is_open is False

    def test_manufacturer_when_closed(self):
        device = HIDRelayDevice(vendor_id=0x16C0, product_id=0x05DF)
        assert device.manufacturer == "Unknown"

    def test_product_when_closed(self):
        device = HIDRelayDevice(vendor_id=0x16C0, product_id=0x05DF)
        assert device.product == "Unknown"


class TestHIDRelayDeviceWithoutHardware:
    def test_open_raises_device_not_found(self):
        device = HIDRelayDevice(vendor_id=0x0000, product_id=0x0000)
        with pytest.raises(DeviceNotFoundError):
            device.open()

    def test_set_channel_without_open_raises(self):
        device = HIDRelayDevice(vendor_id=0x16C0, product_id=0x05DF)
        with pytest.raises(DeviceConnectionError, match="not open"):
            device.set_channel(1, True)

    def test_close_when_not_open_is_safe(self):
        device = HIDRelayDevice(vendor_id=0x16C0, product_id=0x05DF)
        device.close()


class TestMockRelayDevice:
    def test_open_sets_is_open(self):
        device = MockRelayDevice()
        device.open()
        assert device.is_open is True

    def test_close_clears_is_open(self):
        device = MockRelayDevice()
        device.open()
        device.close()
        assert device.is_open is False

    def test_set_channel_tracks_state(self):
        device = MockRelayDevice(channels=2)
        device.open()
        device.set_channel(1, True)
        assert device._states[1] is True

    def test_set_channel_off(self):
        device = MockRelayDevice(channels=2)
        device.open()
        device.set_channel(1, True)
        device.set_channel(1, False)
        assert device._states[1] is False

    def test_set_channel_when_closed_raises(self):
        device = MockRelayDevice()
        with pytest.raises(DeviceConnectionError, match="not open"):
            device.set_channel(1, True)

    def test_manufacturer_when_open(self):
        device = MockRelayDevice()
        device.open()
        assert device.manufacturer == "MockManufacturer"

    def test_manufacturer_when_closed(self):
        device = MockRelayDevice()
        assert device.manufacturer == "Unknown"

    def test_product_when_open(self):
        device = MockRelayDevice()
        device.open()
        assert device.product == "MockRelay"

    def test_product_when_closed(self):
        device = MockRelayDevice()
        assert device.product == "Unknown"

    def test_custom_channel_count(self):
        device = MockRelayDevice(channels=4)
        device.open()
        assert len(device._states) == 4

    def test_open_initializes_all_channels_off(self):
        device = MockRelayDevice(channels=3)
        device.open()
        assert all(v is False for v in device._states.values())
