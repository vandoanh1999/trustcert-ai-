# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched Metadata Lookup in Vector Store
**Learning:** Individual SQL queries for each result in a vector search (N+1 pattern) cause significant overhead. Batched lookups using `WHERE idx IN (...)` reduced search latency by ~70% (from ~2.5ms to ~0.7ms per search). Additionally, using a `set` for duplicate checks in the `save` method ensures O(1) membership testing as the store scales.
**Action:** Identify N+1 query patterns in storage or network layers and refactor them into batched operations. Use sets for frequent membership checks on large lists.
