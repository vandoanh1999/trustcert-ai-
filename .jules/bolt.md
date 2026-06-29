# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched Metadata Retrieval
**Learning:** Performing individual SQLite lookups for each item in a vector search result set (the N+1 query problem) creates a significant I/O bottleneck. Transitioning to a single `SELECT ... WHERE idx IN (...)` query and mapping results in-memory yields a ~3.4x performance improvement for typical search parameters (top_k=50).
**Action:** Always batch database lookups when processing lists of identifiers to minimize round-trip overhead.
