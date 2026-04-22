# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Reputation Data Caching
**Learning:** Frequent disk I/O and JSON parsing for small configuration or state files (like reputation DBs) can significantly throttle performance in hot paths (like inference or validation). Implementing a simple in-memory cache with an O(1) dictionary lookup can reduce latency by orders of magnitude (~100x in this case).
**Action:** Use global in-memory caches for frequently accessed persistent data, ensuring thread safety and data integrity by returning copies of the cached data.
