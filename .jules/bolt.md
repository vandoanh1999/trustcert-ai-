# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched Metadata Retrieval
**Learning:** The N+1 query problem in vector search (fetching metadata individually for each FAISS result) causes significant latency overhead due to repeated SQLite roundtrips. Batching these requests into a single `IN` query improves search throughput by ~48%.
**Action:** When retrieving metadata for a list of search results, use a single batched query with an `IN` clause instead of iterating and querying individually.
