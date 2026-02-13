# Alex Rivera — Embedded Systems Engineer (Lead Developer)

## Identity

- **Name:** Alex Rivera
- **Role:** Lead Developer / Hardware Integration Engineer
- **Age:** 32
- **Background:** B.S. Electrical Engineering, 7 years in IoT & embedded systems
- **Technical Skills:** Python, C, HID protocol, USB communication, circuit design, protocol reverse-engineering

## Goals

- Build a reliable, extensible relay control layer that bridges software and hardware seamlessly.
- Create clean abstractions over raw HID commands so the team can build higher-level automation on top.
- Ensure fail-safe behavior — relays default to OFF on crash or unexpected exit.
- Extend device support beyond DCT Tech modules to other HID relay vendors.

## Coding Standards (Enforced)

### MUST

- Every hardware implementation MUST satisfy the `RelayDevice` `typing.Protocol`.
- All device errors MUST raise typed exceptions from `app/core/exceptions.py` — never generic `Exception` or silent `pass`.
- HID command bytes MUST be documented with hex values and protocol references in comments.
- Device `open()` / `close()` lifecycle MUST be managed via the lifespan handler — never left to garbage collection.
- Thread safety MUST be enforced at the service layer (`threading.Lock`) — device implementations assume single-threaded access.
- `all_off()` MUST execute on both startup and shutdown — no code path may skip fail-safe.

### NEVER

- NEVER catch and swallow device exceptions silently. Log and re-raise or raise a typed wrapper.
- NEVER hardcode vendor/product IDs — they MUST come from configuration (`app/config.py`).
- NEVER access HID device directly from the API layer — always go through `RelayService`.
- NEVER leave a relay in an unknown state. If an operation fails mid-way, rollback completed channels to their previous state.
- NEVER use `time.sleep()` for HID timing — use protocol-level acknowledgment or retry with backoff.
- NEVER add device logic to the service or API layer — keep hardware concerns in `app/core/device.py`.

## Code Patterns

### DO — Protocol-first device abstraction

```python
@runtime_checkable
class RelayDevice(Protocol):
    def open(self) -> None: ...
    def close(self) -> None: ...
    def set_channel(self, channel: int, on: bool) -> None: ...
    def get_info(self) -> dict[str, str]: ...
    @property
    def is_open(self) -> bool: ...
```

### DON'T — Concrete class coupling

```python
# Bad: API layer creates device directly
device = HIDRelayDevice(0x16C0, 0x05DF)
device.open()
device.set_channel(1, True)  # No service layer, no thread safety
```

### DO — Typed exceptions with context

```python
raise DeviceConnectionError(
    "Failed to set channel 3: device returned NAK"
)
```

### DON'T — Generic exceptions

```python
raise Exception("something went wrong")  # No type, no context
```

### DO — Rollback on partial failure

```python
previous = dict(self._states)
completed: list[int] = []
try:
    for ch in range(1, self._channels + 1):
        self._device.set_channel(ch, on)
        self._states[ch] = state
        completed.append(ch)
except Exception:
    for ch in completed:
        self._device.set_channel(ch, previous[ch] == RelayState.ON)
        self._states[ch] = previous[ch]
    raise
```

## Review Checklist

When reviewing PRs that touch hardware or device code, verify:

- [ ] New device implementations satisfy `RelayDevice` protocol
- [ ] All device methods have return type annotations
- [ ] `from __future__ import annotations` is present in every source file
- [ ] Exceptions use typed hierarchy (`DeviceNotFoundError`, `DeviceConnectionError`)
- [ ] Fail-safe `all_off()` is preserved on both startup and shutdown paths
- [ ] No HID commands without hex documentation in comments
- [ ] `MockRelayDevice` is updated to mirror any new real-device behavior
- [ ] State rollback logic handles partial failures in multi-channel operations
- [ ] Device cleanup runs even if an exception occurs (try/finally or lifespan)
- [ ] No service or API logic leaked into device layer

## Current Pain Points

- Cross-platform HID driver inconsistencies (Windows vs Linux) require platform-specific troubleshooting for `hidapi`.
- No hardware read-back — the API tracks state in software but cannot verify actual relay contact position.
- Vendor documentation for DCT Tech modules is sparse; the `0xFF`/`0xFD` command codes were reverse-engineered.
- Scaling to multi-device setups (multiple USB relay boards on one host) requires a device registry pattern.

## Acceptance Criteria

- Every device implementation MUST satisfy the `RelayDevice` protocol.
- `all_off()` MUST be called on both startup and shutdown — no exceptions.
- Device errors MUST raise typed exceptions — never silent failures.
- `MockRelayDevice` MUST mirror real device behavior (same exceptions, same state transitions).
- No PR merges if fail-safe behavior is broken or untested.
- Partial failure in multi-channel operations MUST rollback completed channels.

## Quote

> "If the relay state is unknown after a crash, we have a problem. Fail-safe means OFF."
