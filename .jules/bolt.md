# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Vector Store O(N) Bottlenecks
**Learning:** Checking for duplicate vector IDs using list membership is $O(N)$ and scales poorly. Similarly, fetching metadata for each search result using individual SQL queries creates an $N+1$ query problem, increasing latency due to database roundtrips.
**Action:** Use an in-memory `set` for $O(1)$ duplicate checks and a single batched SQL `IN` query to retrieve metadata for all search results at once.
