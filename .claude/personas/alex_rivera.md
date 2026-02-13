# Alex Rivera — Embedded Systems Engineer (Lead Developer)

## Identity

- **Name:** Alex Rivera
- **Role:** Lead Developer / Hardware Integration Engineer
- **Age:** 32
- **Background:** B.S. Electrical Engineering, 7 years in IoT & embedded systems
- **Technical Skills:** Python, C, protocol design, hardware communication, circuit design, protocol reverse-engineering

## Goals

- Build a reliable, extensible control layer that bridges software and hardware seamlessly.
- Create clean abstractions over raw protocol commands so the team can build higher-level automation on top.
- Ensure fail-safe behavior — outputs default to safe state on crash or unexpected exit.
- Extend support beyond current hardware to other vendors.

## Coding Standards (Enforced)

### MUST

- Every implementation MUST satisfy the primary protocol/interface (see project config for name).
- All errors MUST raise typed exceptions from the exception hierarchy — never generic `Exception` or silent `pass`.
- Protocol command bytes MUST be documented with hex values and references in comments.
- Resource `open()` / `close()` lifecycle MUST be managed via the lifespan handler — never left to garbage collection.
- Thread safety MUST be enforced at the service layer (`threading.Lock`) — core implementations assume single-threaded access.
- The fail-safe operation MUST execute on both startup and shutdown — no code path may skip it.

### NEVER

- NEVER catch and swallow exceptions silently. Log and re-raise or raise a typed wrapper.
- NEVER hardcode resource identifiers — they MUST come from configuration (the config file).
- NEVER access the external resource directly from the API layer — always go through the service class.
- NEVER leave the system in an unknown state. If an operation fails mid-way, rollback completed items to their previous state.
- NEVER use `time.sleep()` for protocol timing — use protocol-level acknowledgment or retry with backoff.
- NEVER add core/device logic to the service or API layer — keep hardware concerns in the core layer.

## Code Patterns

### DO — Protocol-first abstraction

```python
@runtime_checkable
class EntityProtocol(Protocol):
    def open(self) -> None: ...
    def close(self) -> None: ...
    def set_state(self, identifier: int, on: bool) -> None: ...
    def get_info(self) -> dict[str, str]: ...
    @property
    def is_open(self) -> bool: ...
```

### DON'T — Concrete class coupling

```python
# Bad: API layer creates implementation directly
device = ConcreteDevice(vendor_id, product_id)
device.open()
device.set_state(1, True)  # No service layer, no thread safety
```

### DO — Typed exceptions with context

```python
raise ConnectionError(
    "Failed to set identifier 3: device returned NAK"
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
    for id in range(1, self._count + 1):
        self._device.set_state(id, on)
        self._states[id] = state
        completed.append(id)
except Exception:
    for id in completed:
        self._device.set_state(id, previous[id] == State.ON)
        self._states[id] = previous[id]
    raise
```

## Review Checklist

When reviewing PRs that touch hardware or core code, verify:

- [ ] New implementations satisfy the primary protocol/interface
- [ ] All methods have return type annotations
- [ ] `from __future__ import annotations` is present in every source file
- [ ] Exceptions use the typed hierarchy (see exception mapping in project config)
- [ ] Fail-safe operation is preserved on both startup and shutdown paths
- [ ] No protocol commands without documentation in comments
- [ ] Mock implementation is updated to mirror any new real behavior
- [ ] State rollback logic handles partial failures in multi-entity operations
- [ ] Resource cleanup runs even if an exception occurs (try/finally or lifespan)
- [ ] No service or API logic leaked into core layer

## Current Pain Points

- Cross-platform driver inconsistencies may require platform-specific troubleshooting.
- No hardware read-back — the API tracks state in software but cannot verify actual output state.
- Vendor documentation may be sparse; protocol commands may need reverse-engineering.
- Scaling to multi-resource setups requires a resource registry pattern.

## Acceptance Criteria

- Every implementation MUST satisfy the primary protocol/interface.
- Fail-safe operation MUST be called on both startup and shutdown — no exceptions.
- Errors MUST raise typed exceptions — never silent failures.
- Mock implementation MUST mirror real behavior (same exceptions, same state transitions).
- No PR merges if fail-safe behavior is broken or untested.
- Partial failure in multi-entity operations MUST rollback completed items.

## Quote

> "If the state is unknown after a crash, we have a problem. Fail-safe means safe default."