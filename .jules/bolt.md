# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2026-07-04 - Batched SQL Lookups in Vector Search
**Learning:** Performing individual SQL queries in a loop for metadata retrieval during vector search creates a significant bottleneck due to database roundtrip overhead. Batching these queries using an `IN` clause reduces latency by ~60-70%.
**Action:** Always batch database lookups when retrieving metadata for multiple search results. Use mapping dictionaries for O(1) retrieval of fetched rows.
