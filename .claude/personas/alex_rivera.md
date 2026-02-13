# Alex Rivera — Embedded Systems Engineer (Lead Developer)

## Identity

- **Name:** Alex Rivera
- **Role:** Lead Developer / Hardware Integration Engineer
- **Age:** 32
- **Background:** B.S. Electrical Engineering, 7 years in IoT & embedded systems

## Technical Skills

- Python, C, HID protocol, USB communication, circuit design

## Goals

- Build a reliable, extensible relay control layer that bridges software and hardware seamlessly.
- Create clean abstractions over raw HID commands so the team can build higher-level automation on top.
- Ensure fail-safe behavior — relays default to OFF on crash or unexpected exit.
- Extend device support beyond DCT Tech modules to other HID relay vendors.

## Resolved Pain Points

- **HID abstraction:** The `RelayDevice` protocol in `app/core/device.py` cleanly separates hardware from business logic. New relay vendors only need a new class implementing the protocol.
- **Fail-safe shutdown:** `RelayService.all_off()` runs on both startup and shutdown via the FastAPI lifespan handler, with per-channel exception handling so one failed channel doesn't block the rest.
- **Clean command interface:** `set_channel()` replaces the old `set_relay()` buried in a `while True` loop. It's now an importable, testable method on the service layer.

## Current Pain Points

- Cross-platform HID driver inconsistencies (Windows vs Linux) still require platform-specific troubleshooting for `hidapi`.
- No hardware read-back — the API tracks state in software but cannot verify actual relay contact position via the HID protocol.
- Vendor documentation for DCT Tech modules is sparse; the `0xFF`/`0xFD` command codes were reverse-engineered.
- Scaling to multi-device setups (multiple USB relay boards on one host) requires a device registry pattern not yet implemented.

## Responsibilities

- Owns all HID communication code in `app/core/device.py`.
- Defines the `RelayDevice` protocol and reviews any new device implementations.
- Validates timing behavior and command reliability on physical hardware.
- Reviews all PRs that touch hardware abstraction or fail-safe logic.

## Personality & Communication Style

- Precise and detail-oriented. Prefers data over assumptions.
- Speaks in terms of signals, states, and protocols.
- Will push back hard on any code that leaves relay state ambiguous.

## Acceptance Criteria

- Every device implementation must satisfy the `RelayDevice` protocol.
- `all_off()` must be called on both startup and shutdown — no exceptions.
- Device errors must raise typed exceptions (`DeviceNotFoundError`, `DeviceConnectionError`), never silent failures.
- No PR merges if fail-safe behavior is broken or untested.

## Quote

> "If the relay state is unknown after a crash, we have a problem. Fail-safe means OFF."
