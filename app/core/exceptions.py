from __future__ import annotations


class RelayError(Exception):
    """Base exception for all relay operations."""


class DeviceNotFoundError(RelayError):
    """Raised when the USB relay device cannot be found or opened."""

    def __init__(self, vendor_id: int, product_id: int):
        self.vendor_id = vendor_id
        self.product_id = product_id
        super().__init__(
            f"Device not found: vendor=0x{vendor_id:04X}, product=0x{product_id:04X}"
        )


class DeviceConnectionError(RelayError):
    """Raised when communication with the device fails."""


class InvalidChannelError(RelayError):
    """Raised when an invalid relay channel is specified."""

    def __init__(self, channel: int, max_channels: int):
        self.channel = channel
        self.max_channels = max_channels
        super().__init__(
            f"Invalid channel {channel}. Must be between 1 and {max_channels}."
        )
