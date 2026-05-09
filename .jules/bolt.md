# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Reputation System Caching
**Learning:** Frequent disk I/O for small JSON databases in hot paths (like reputation lookups during message validation) causes significant latency (~0.5ms per read). Implementing a simple module-level cache with `.copy()` for thread-safety can reduce this latency to the microsecond range (~0.007ms), a ~70x speedup.
**Action:** Use in-memory caches for small, frequently-accessed persistent data structures to bypass filesystem and JSON parsing bottlenecks.
