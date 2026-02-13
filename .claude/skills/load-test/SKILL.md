---
name: load-test
description: Write performance and load tests to validate throughput and thread safety (Priya Sharma's workflow)
disable-model-invocation: true
---

Write performance/load tests for: $ARGUMENTS

## Step 1 — Identify Performance Scenarios
- **Throughput**: How many requests/second can the API handle?
- **Concurrency**: Do concurrent requests cause race conditions or deadlocks?
- **Rate limiting**: Does the rate limiter correctly throttle under load?
- **Rapid state changes**: Can the system handle rapid state cycling without corruption?
- **Response time**: Do endpoints respond within acceptable latency (< 200ms)?

## Step 2 — Write Concurrency Tests
```python
import concurrent.futures

class TestConcurrency:
    def test_concurrent_state_changes_no_race_condition(
        self, client: TestClient
    ) -> None:
        """Verify thread-safe access under concurrent requests."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            futures = []
            for i in range(50):
                # Submit concurrent state-changing requests
                futures.append(pool.submit(make_state_change_request, client, i))
            results = [f.result() for f in futures]

        # All requests should succeed (no 500s from race conditions)
        for resp in results:
            assert resp.status_code == 200

        # Final state should be consistent
```

## Step 3 — Write Rapid State Change Tests
Verify the system handles rapid state changes without corruption.
After rapid cycling, final state should be deterministic and consistent.

## Step 4 — Write Latency Tests
```python
import time

class TestLatency:
    def test_health_endpoint_under_200ms(self, client: TestClient) -> None:
        start = time.perf_counter()
        resp = client.get("<health endpoint path>")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < 200, f"Health took {elapsed_ms:.1f}ms (limit: 200ms)"
```

## Step 5 — Organize
Place load tests in the performance test file (see test file mapping in project config).

## Step 6 — Verify
Run the test command (see project config) — full suite still passes.

## Rules
- Performance tests MUST be deterministic — no flaky assertions based on timing
- Use `time.perf_counter()` not `time.time()` for measurements
- Thread pool tests verify no 500 errors, not specific timing
- Rapid state change tests verify final state consistency