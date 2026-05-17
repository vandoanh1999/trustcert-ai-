# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched Vector Metadata Retrieval
**Learning:** Sequential SQL queries for individual metadata rows during vector search create massive overhead (O(N) queries). Using a single SQL `IN` query to batch metadata retrieval reduces database latency by ~70% for top-k searches.
**Action:** Use SQL `IN` clauses for batch lookups and map results back to FAISS indices to maintain ordering.
