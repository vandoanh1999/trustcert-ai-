# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Reputation Database Caching
**Learning:** Frequent disk I/O and JSON parsing for small, stable datasets (like the reputation DB) significantly increase latency. Implementing a module-level in-memory cache for `load_reputation_db` reduced `get_reputation` latency by ~14x (from 43μs to 3μs).
**Action:** Implement in-memory caches for frequently read configuration or state files, ensuring the cache is invalidated or updated on writes to maintain consistency within the process.
