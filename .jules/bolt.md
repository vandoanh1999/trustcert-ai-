# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched SQL for Vector Metadata
**Learning:** Fetching metadata for top-K vector search results one-by-one (N+1 query problem) creates a massive bottleneck as K increases. Using a single batched SQL `IN` query reduces database round-trip overhead and improves search throughput by ~3.5x.
**Action:** Always check for N+1 query patterns in data retrieval loops and refactor to use batched queries or bulk fetches.

## 2025-05-15 - O(1) Membership Checks for Ingestion
**Learning:** Using a list for duplicate checking during high-frequency ingestion results in O(N) complexity, which degrades performance as the store grows.
**Action:** Use a complementary set for membership checks to maintain O(1) performance while keeping the list for ordered traversal if needed.
