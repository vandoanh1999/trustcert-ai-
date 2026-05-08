# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - In-Memory Caching for Frequent Lookups
**Learning:** Frequent disk I/O and JSON parsing for small, frequently-read databases (like reputation scores) is a massive performance bottleneck. Implementing an in-memory cache with `global` state and `.copy()` for mutation safety reduced lookup latency by ~100x (0.45s down to 0.004s per 1000 calls).
**Action:** Identify small metadata or state files that are read frequently but updated rarely, and implement a transparent in-memory cache with write-through or write-back logic.
