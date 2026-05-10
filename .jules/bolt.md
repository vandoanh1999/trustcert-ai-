# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Vector Store Scale Optimization
**Learning:** O(N) duplicate checks in growing vector storage and per-index SQL queries for metadata retrieval are major bottlenecks that degrade performance linearly as the database grows. Maintaining an in-memory set of IDs and using SQL IN clauses for batched retrieval prevents this degradation.
**Action:** Always use in-memory sets for membership checks in storage layers and batch database lookups to minimize round-trip overhead.
