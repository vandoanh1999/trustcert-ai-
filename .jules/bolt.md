# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched SQL Metadata Retrieval
**Learning:** Performing individual SQL queries for each item in a search result set (N+1 problem) introduces significant latency due to repeated database round-trips. Batching these into a single `SELECT ... WHERE idx IN (...)` query and using an in-memory map to restore order yields a ~2.8x - 3x throughput improvement for vector searches.
**Action:** Always batch database lookups when processing lists of results to minimize I/O overhead.
