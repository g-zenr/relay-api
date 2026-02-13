---
name: add-device
description: Add a new relay device implementation (Alex Rivera's workflow)
disable-model-invocation: true
---

Add a new relay device implementation: $ARGUMENTS

Follow Alex Rivera's hardware integration standards:

1. **Study the protocol**: Read `app/core/device.py` to understand the `RelayDevice` Protocol:
   ```python
   class RelayDevice(Protocol):
       def open(self) -> None: ...
       def close(self) -> None: ...
       def set_channel(self, channel: int, on: bool) -> None: ...
       def get_info(self) -> dict[str, str]: ...
       @property
       def is_open(self) -> bool: ...
   ```

2. **Implement the device class** in `app/core/device.py`:
   - MUST satisfy `RelayDevice` Protocol — verify with `isinstance(device, RelayDevice)`
   - `from __future__ import annotations` at top of file
   - All methods MUST have return type annotations
   - Document HID command bytes with hex values in comments
   - Raise `DeviceNotFoundError` if device not detected on `open()`
   - Raise `DeviceConnectionError` on communication failures
   - Track `is_open` state accurately
   - `close()` MUST be idempotent — safe to call multiple times

3. **Update config** if new settings are needed:
   - Add to `app/config.py` Settings class with `RELAY_` prefix
   - Document in `.env.example` with defaults and description

4. **Update MockRelayDevice** to mirror any new behavior:
   - Same exceptions for same error conditions
   - Same state transitions

5. **Wire into lifespan** in `app/main.py`:
   - Add device selection logic in the `lifespan()` function
   - Ensure `all_off()` runs on both startup and shutdown for the new device

6. **Write tests** in `tests/test_core_device.py`:
   - Test `open()` / `close()` lifecycle
   - Test `set_channel()` for valid and invalid channels
   - Test `get_info()` returns expected structure
   - Test error conditions raise typed exceptions
   - Test `is_open` property accuracy

7. **Verify**: Run `python -m pytest tests/ -v --tb=short` and `python -m mypy app/`
