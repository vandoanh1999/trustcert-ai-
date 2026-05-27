# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched Metadata Retrieval in FVS
**Learning:** Performing individual SQL queries for each FAISS search result (N+1 query problem) creates a significant I/O bottleneck. Implementing batched metadata retrieval using a single SQLite `IN` query improves search throughput by ~69%.
**Action:** Always use batched queries when mapping external index results (like FAISS or custom ID lists) back to database records to minimize database roundtrips.
