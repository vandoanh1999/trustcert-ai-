## 2026-04-10 - [In-Memory Cache for Reputation]
**Learning:** Frequent disk I/O and JSON parsing for reputation lookups were causing significant latency (~96µs). Implementing a simple in-memory cache with isolation (using .copy()) and write-safety (cache update after successful disk write) reduced latency by ~146x (~0.66µs).
**Action:** Always prefer in-memory caches for frequently read metadata, but ensure isolation via deep/shallow copies to prevent accidental shared state side effects.
