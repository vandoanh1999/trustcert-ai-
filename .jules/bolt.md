# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Reputation Lookup Caching
**Learning:** Frequent disk I/O for reading small JSON configuration/state files (like reputation scores) can become a significant bottleneck as the network grows. Implementing a simple in-memory cache with synchronization on writes can reduce latency by multiple orders of magnitude. Using `.copy()` when returning cached dicts is essential to prevent accidental mutation of the global state.
**Action:** Implement in-memory caching for frequently accessed but slowly changing state files, ensuring data integrity with `.copy()` and immediate write-through to disk.
