# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched Metadata Retrieval in Vector Stores
**Learning:** Executing individual SQL queries for each result in a vector search (N+1 query problem) creates a significant bottleneck due to database round-trip overhead. Using a single `IN` query to fetch all metadata at once can improve search throughput by 3-4x for typical `top_k` values.
**Action:** Use batched database queries whenever multiple related records need to be retrieved, and use a hash map to re-order the results if the original sequence must be preserved.
