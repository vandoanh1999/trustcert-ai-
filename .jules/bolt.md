# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Reputation DB Caching
**Learning:** Frequent disk I/O in the trust layer () scales poorly with network activity. Implementing a global in-memory cache reduced latency from ~0.04ms to ~0.0002ms (~200x speedup). Returning a  of the cache is essential to prevent unintended mutations by external callers.
**Action:** Use in-memory caching for frequently accessed read-only or EMA-updated JSON "databases" in the P2P and Trust layers, always returning copies for safety.

## 2025-05-15 - Reputation DB Caching
**Learning:** Frequent disk I/O in the trust layer (`get_reputation`) scales poorly with network activity. Implementing a global in-memory cache reduced latency from ~0.04ms to ~0.0002ms (~200x speedup). Returning a `.copy()` of the cache is essential to prevent unintended mutations by external callers.
**Action:** Use in-memory caching for frequently accessed read-only or EMA-updated JSON "databases" in the P2P and Trust layers, always returning copies for safety.
