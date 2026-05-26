# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-26 - Batched Vector Metadata Retrieval & Commits
**Learning:** Synchronous SQLite commits on every insertion create a massive I/O bottleneck, while individual SQL queries for each search result (N+1 problem) degrade search performance. Batching commits and using SQL 'IN' clauses for metadata retrieval provides a ~92% speedup in ingestion and ~54% reduction in search latency.
**Action:** Always batch database commits in high-throughput storage layers and use batched queries to retrieve metadata for multiple indices simultaneously.
