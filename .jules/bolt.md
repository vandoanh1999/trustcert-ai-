# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Reputation Cache
**Learning:** Frequent reads from a JSON-based reputation database cause significant overhead due to disk I/O and JSON parsing (~0.5ms per call). Implementing a simple in-memory cache with synchronization on writes reduces lookup latency to O(1) in-memory access (~0.006ms), providing an 80x+ speedup.
**Action:** For read-heavy configuration or state files that fit in memory, implement a write-through cache to eliminate redundant I/O. Use `.copy()` when returning cached dictionaries to prevent accidental external mutation.
