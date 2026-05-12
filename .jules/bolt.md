# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2026-05-12 - In-Memory Reputation Caching
**Learning:** Frequent JSON disk I/O for small lookup tables (like reputation scores) can become a significant bottleneck as the expert pool grows. In-memory caching with a simple `.copy()` pattern provides O(1) access while maintaining data integrity and durability.
**Action:** Implement module-level caching for frequently accessed JSON metadata stores to eliminate redundant I/O and parsing overhead.
