from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.api.dependencies import get_relay_service, require_device
from app.core.exceptions import DeviceConnectionError, InvalidChannelError
from app.models.schemas import (
    BurnTestRequest,
    BurnTestStatus,
    DeviceInfo,
    ErrorResponse,
    RelayAllStatus,
    RelayBulkCommand,
    RelayCommand,
    RelayStatus,
)
from app.services.relay_service import RelayService

router = APIRouter(prefix="/relays", tags=["Relays"])


# --- Static routes first (before /{channel} path parameter) ---


@router.get(
    "/device/info",
    response_model=DeviceInfo,
    summary="Get USB device information",
    description="Returns the USB manufacturer string, product string, "
    "total channel count, and live connection status of the relay module.",
)
def get_device_info(
    service: RelayService = Depends(get_relay_service),
) -> DeviceInfo:
    return service.get_device_info()


# --- Burn test routes ---


@router.post(
    "/burn-test",
    response_model=BurnTestStatus,
    summary="Start relay burn test",
    description="Starts a background burn test. Mode 'all' cycles every relay ON/OFF "
    "together. Mode 'alternate' switches relay 1 and relay 2 back and forth. "
    "Set cycles to 0 for indefinite cycling (stop manually).",
    responses={
        409: {
            "model": ErrorResponse,
            "description": "Burn test is already running",
        },
        503: {
            "model": ErrorResponse,
            "description": "USB relay device is not connected",
        },
    },
    tags=["Burn Test"],
)
def start_burn_test(
    request: BurnTestRequest,
    service: RelayService = Depends(require_device),
) -> BurnTestStatus:
    status = service.get_burn_test_status()
    if status.running:
        raise HTTPException(
            status_code=409,
            detail="Burn test is already running. Stop it first.",
        )
    return service.start_burn_test(request.cycles, request.delay_ms, request.mode)


@router.get(
    "/burn-test",
    response_model=BurnTestStatus,
    summary="Get burn test status",
    description="Returns the current status of the burn test including "
    "cycles completed, target, and error count.",
    tags=["Burn Test"],
)
def get_burn_test_status(
    service: RelayService = Depends(get_relay_service),
) -> BurnTestStatus:
    return service.get_burn_test_status()


@router.delete(
    "/burn-test",
    response_model=BurnTestStatus,
    summary="Stop burn test",
    description="Stops a running burn test and turns all relays OFF (fail-safe).",
    tags=["Burn Test"],
)
def stop_burn_test(
    service: RelayService = Depends(require_device),
) -> BurnTestStatus:
    return service.stop_burn_test()


# --- Collection routes ---


@router.get(
    "",
    response_model=RelayAllStatus,
    summary="Get all relay states",
    description="Returns the current ON/OFF state of every relay channel.",
)
def get_all_relays(
    service: RelayService = Depends(get_relay_service),
) -> RelayAllStatus:
    return RelayAllStatus(channels=service.get_all_channels())


@router.put(
    "",
    response_model=RelayAllStatus,
    summary="Set all relays to the same state",
    description="Sets every relay channel to the same state in a single "
    "atomic operation. Useful for emergency shutoff (`off`) or powering "
    "all channels simultaneously (`on`).",
    responses={
        502: {
            "model": ErrorResponse,
            "description": "USB device communication failure",
        },
        503: {
            "model": ErrorResponse,
            "description": "USB relay device is not connected",
        },
    },
)
def set_all_relays(
    command: RelayBulkCommand,
    service: RelayService = Depends(require_device),
) -> RelayAllStatus:
    try:
        channels = service.set_all_channels(command.state)
    except DeviceConnectionError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    return RelayAllStatus(channels=channels)


# --- Single channel routes ---


@router.get(
    "/{channel}",
    response_model=RelayStatus,
    summary="Get a single relay state",
    description="Returns the current ON/OFF state for the specified channel.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Channel number is out of range",
        },
    },
)
def get_relay(
    channel: int = Path(ge=1, description="Relay channel number (1-based)"),
    service: RelayService = Depends(get_relay_service),
) -> RelayStatus:
    try:
        return service.get_channel(channel)
    except InvalidChannelError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put(
    "/{channel}",
    response_model=RelayStatus,
    summary="Set a single relay state",
    description="Sends a HID feature report to switch the specified relay "
    "channel ON or OFF. Returns the confirmed new state.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Channel number is out of range",
        },
        502: {
            "model": ErrorResponse,
            "description": "USB device communication failure",
        },
        503: {
            "model": ErrorResponse,
            "description": "USB relay device is not connected",
        },
    },
)
def set_relay(
    command: RelayCommand,
    channel: int = Path(ge=1, description="Relay channel number (1-based)"),
    service: RelayService = Depends(require_device),
) -> RelayStatus:
    try:
        return service.set_channel(channel, command.state)
    except InvalidChannelError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    except DeviceConnectionError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc))
