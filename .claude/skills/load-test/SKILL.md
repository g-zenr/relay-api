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
- **Rapid toggling**: Can the device handle rapid ON/OFF cycling without corruption?
- **Response time**: Do endpoints respond within acceptable latency (< 200ms)?

## Step 2 — Write Concurrency Tests
```python
import concurrent.futures

class TestConcurrency:
    def test_concurrent_set_channel_no_race_condition(
        self, client: TestClient
    ) -> None:
        """Verify thread-safe access under concurrent requests."""
        def toggle_channel(channel: int, state: str):
            return client.put(
                f"/api/v1/relays/{channel}",
                json={"state": state},
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            futures = []
            for i in range(50):
                ch = (i % 2) + 1
                state = "on" if i % 2 == 0 else "off"
                futures.append(pool.submit(toggle_channel, ch, state))

            results = [f.result() for f in futures]

        # All requests should succeed (no 500s from race conditions)
        for resp in results:
            assert resp.status_code == 200

        # Final state should be consistent
        resp = client.get("/api/v1/relays")
        assert resp.status_code == 200
```

## Step 3 — Write Rapid Toggle Tests
```python
class TestRapidToggle:
    def test_rapid_on_off_cycling(self, client: TestClient) -> None:
        """Verify device handles rapid state changes without corruption."""
        for _ in range(100):
            client.put("/api/v1/relays/1", json={"state": "on"})
            client.put("/api/v1/relays/1", json={"state": "off"})

        # State should be deterministic after rapid cycling
        resp = client.get("/api/v1/relays/1")
        assert resp.status_code == 200
        assert resp.json()["state"] == "off"
```

## Step 4 — Write Latency Tests
```python
import time

class TestLatency:
    def test_health_endpoint_under_200ms(self, client: TestClient) -> None:
        start = time.perf_counter()
        resp = client.get("/health")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert resp.status_code == 200
        assert elapsed_ms < 200, f"Health took {elapsed_ms:.1f}ms (limit: 200ms)"
```

## Step 5 — Organize
Place load tests in `tests/test_performance.py` (separate from unit/integration tests).

## Step 6 — Verify
```bash
python -m pytest tests/test_performance.py -v --tb=short
python -m pytest tests/ -v --tb=short  # Full suite still passes
```

## Rules
- Performance tests MUST be deterministic — no flaky assertions based on timing
- Use `time.perf_counter()` not `time.time()` for measurements
- Thread pool tests verify no 500 errors, not specific timing
- Rapid toggle tests verify final state consistency
