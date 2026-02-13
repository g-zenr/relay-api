from app.core.exceptions import (
    DeviceConnectionError,
    DeviceNotFoundError,
    InvalidChannelError,
    RelayError,
)


class TestExceptionHierarchy:
    def test_all_exceptions_inherit_from_relay_error(self):
        assert issubclass(DeviceNotFoundError, RelayError)
        assert issubclass(DeviceConnectionError, RelayError)
        assert issubclass(InvalidChannelError, RelayError)

    def test_relay_error_is_base_exception(self):
        assert issubclass(RelayError, Exception)


class TestDeviceNotFoundError:
    def test_message_includes_hex_ids(self):
        exc = DeviceNotFoundError(vendor_id=0x16C0, product_id=0x05DF)
        assert "0x16C0" in str(exc)
        assert "0x05DF" in str(exc)

    def test_stores_ids(self):
        exc = DeviceNotFoundError(vendor_id=0x16C0, product_id=0x05DF)
        assert exc.vendor_id == 0x16C0
        assert exc.product_id == 0x05DF


class TestDeviceConnectionError:
    def test_accepts_message(self):
        exc = DeviceConnectionError("connection lost")
        assert str(exc) == "connection lost"


class TestInvalidChannelError:
    def test_message_includes_channel_and_max(self):
        exc = InvalidChannelError(channel=5, max_channels=2)
        assert "5" in str(exc)
        assert "1" in str(exc)
        assert "2" in str(exc)

    def test_stores_values(self):
        exc = InvalidChannelError(channel=0, max_channels=4)
        assert exc.channel == 0
        assert exc.max_channels == 4
