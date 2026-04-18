# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Reputation Cache Optimization
**Learning:** Implementing in-memory caching in aurora_trust/reputation_vc.py improved get_reputation performance by ~18x (from 0.11ms to 0.006ms) by eliminating redundant disk I/O. Validating the cache against os.path.getmtime() ensures consistency in multi-process environments while maintaining high performance.
**Action:** Use time-based or mtime-based cache invalidation for frequently accessed local JSON data stores to minimize disk latency.
