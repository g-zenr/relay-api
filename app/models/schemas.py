from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RelayState(str, Enum):
    ON = "on"
    OFF = "off"


class BurnTestMode(str, Enum):
    ALL = "all"
    ALTERNATE = "alternate"


class RelayCommand(BaseModel):
    """Command to set a single relay channel state."""

    model_config = {"json_schema_extra": {"examples": [{"state": "on"}]}}

    state: RelayState = Field(
        description="Desired relay state: 'on' or 'off'"
    )


class RelayStatus(BaseModel):
    """Current state of a single relay channel."""

    model_config = {
        "json_schema_extra": {
            "examples": [{"channel": 1, "state": "off"}]
        }
    }

    channel: int = Field(ge=1, description="Relay channel number (1-based)")
    state: RelayState = Field(description="Current relay state")


class RelayBulkCommand(BaseModel):
    """Command to set all relay channels to the same state."""

    model_config = {"json_schema_extra": {"examples": [{"state": "off"}]}}

    state: RelayState = Field(
        description="Desired state for all relay channels"
    )


class DeviceInfo(BaseModel):
    """USB relay device hardware information."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "manufacturer": "www.dcttech.com",
                    "product": "USBRelay2",
                    "channels": 2,
                    "connected": True,
                }
            ]
        }
    }

    manufacturer: str = Field(description="Device manufacturer string")
    product: str = Field(description="Device product string")
    channels: int = Field(ge=1, description="Number of relay channels")
    connected: bool = Field(description="Whether the device is currently connected")


class HealthResponse(BaseModel):
    """API health check response."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "ok",
                    "device_connected": True,
                    "version": "1.0.0",
                }
            ]
        }
    }

    status: str = Field(description="API status")
    device_connected: bool = Field(description="USB device connection state")
    version: str = Field(description="API version")


class ErrorResponse(BaseModel):
    """Standard error response body."""

    model_config = {
        "json_schema_extra": {
            "examples": [{"detail": "Device not found: vendor=0x16C0, product=0x05DF"}]
        }
    }

    detail: str = Field(description="Human-readable error message")


class RelayAllStatus(BaseModel):
    """State of all relay channels."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "channels": [
                        {"channel": 1, "state": "off"},
                        {"channel": 2, "state": "off"},
                    ]
                }
            ]
        }
    }

    channels: list[RelayStatus] = Field(description="List of all channel states")


class BurnTestRequest(BaseModel):
    """Request to start a relay burn test."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"cycles": 100, "delay_ms": 500, "mode": "all"},
                {"cycles": 0, "delay_ms": 300, "mode": "alternate"},
            ]
        }
    }

    cycles: int = Field(
        default=0,
        ge=0,
        description="Number of cycles to run. 0 = run indefinitely until stopped.",
    )
    delay_ms: int = Field(
        default=500,
        ge=100,
        le=60000,
        description="Delay in milliseconds between each state change (min 100ms).",
    )
    mode: BurnTestMode = Field(
        default=BurnTestMode.ALL,
        description="Test mode: 'all' cycles every channel ON/OFF together, "
        "'alternate' switches relay 1 and relay 2 back and forth.",
    )


class BurnTestStatus(BaseModel):
    """Current status of a burn test."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "running": True,
                    "cycles_completed": 42,
                    "cycles_target": 100,
                    "errors": 0,
                    "mode": "all",
                }
            ]
        }
    }

    running: bool = Field(description="Whether the burn test is currently active")
    cycles_completed: int = Field(description="Number of ON/OFF cycles completed")
    cycles_target: int = Field(
        description="Target number of cycles (0 = indefinite)"
    )
    errors: int = Field(description="Number of errors encountered during the test")
    mode: BurnTestMode = Field(
        default=BurnTestMode.ALL,
        description="Current burn test mode",
    )
