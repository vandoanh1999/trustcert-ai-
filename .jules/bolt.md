# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched Metadata Retrieval in FVS
**Learning:** Performing individual SQLite queries for each vector search result (N+1 query problem) creates a significant bottleneck as the result set (top_k) grows. Batching metadata retrieval into a single "WHERE idx IN (...)" query reduces database overhead and improves search throughput by ~3.4x for top_k=100.
**Action:** Always batch database lookups when processing results from an index or search operation to minimize round-trip latency.
