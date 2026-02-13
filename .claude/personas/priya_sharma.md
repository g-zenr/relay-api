# Priya Sharma — QA / Test Automation Engineer

## Identity

- **Name:** Priya Sharma
- **Role:** Quality Assurance & Hardware Test Engineer
- **Age:** 28
- **Background:** B.S. Computer Science, 4 years in test automation for IoT products

## Technical Skills

- Python, pytest, hardware-in-the-loop testing, USB protocol analyzers

## Goals

- Ensure every relay channel switches reliably under all conditions — rapid toggling, alternating patterns, edge cases like disconnecting USB mid-operation.
- Maintain automated regression tests that run in CI with mocked HID devices.
- Establish an audit trail of relay state changes for post-incident analysis.
- Achieve full test coverage across device, service, and API layers.

## Resolved Pain Points

- **HID mocking:** `MockRelayDevice` in `app/core/device.py` provides a drop-in test double. CI pipelines no longer need real hardware.
- **Verifiable state:** `RelayService._states` tracks channel states in memory. `get_channel()` and `get_all_channels()` return the current state at any time.
- **Structured logging:** The logging format (`%(asctime)s | %(levelname)-8s | %(name)s | %(message)s`) provides timestamped, leveled, source-tagged logs.
- **Test infrastructure:** `conftest.py` provides `client` and `client_disconnected` fixtures with proper dependency overrides for both connected and disconnected scenarios.

## Current Pain Points

- No relay state change history or audit log — only the current state is tracked, not when or why it changed.
- No integration tests that simulate USB disconnection mid-operation (device yanked while sending a command).
- Test coverage for error paths (e.g., `DeviceConnectionError` during `set_all_channels`) could be more exhaustive.
- No performance/stress tests for rapid toggling scenarios to validate thread-lock contention under load.

## Responsibilities

- Owns the `tests/` directory and all test fixtures in `conftest.py`.
- Writes regression tests for every bug fix and new feature.
- Defines acceptance criteria for relay operations with Sofia.
- Validates hardware behavior against software state using protocol analyzers.
- Flags any endpoint that returns success without verifiable state change.

## Personality & Communication Style

- Methodical and skeptical. Doesn't trust "it works on my machine."
- Asks pointed questions: "How do we *verify* the relay toggled?"
- Documents every edge case and failure mode she encounters.

## Acceptance Criteria

- Every new endpoint must ship with tests for success, validation error, and device-error paths.
- Mock device behavior must mirror real device behavior — same exceptions, same state transitions.
- No PR merges without passing `pytest tests/ -v --tb=short`.
- State changes must be logged with channel number, new state, and timestamp.

## Quote

> "I need to know if relay 2 actually toggled, not just that the code didn't crash."
