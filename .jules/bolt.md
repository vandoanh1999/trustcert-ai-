# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-06-27 - Batched Metadata Retrieval in FVS
**Learning:** Performing individual SQL queries for each result in a vector search (N+1 anti-pattern) causes significant latency, especially as `top_k` increases. Using a single SQL `IN` query to fetch all metadata at once improved search throughput by ~3.7x for `top_k=100`.
**Action:** Always batch database lookups when processing results from external indices like FAISS.

## 2025-06-27 - O(1) Ingestion Validation
**Learning:** Using list membership checks (`if id in list`) for duplicate validation during ingestion leads to linear performance degradation (O(N)). Introducing a parallel set for tracking IDs improved check throughput by ~10x (from 40k to 393k checks/s).
**Action:** Use sets or hash maps for membership checks in hot paths involving growing data structures.
