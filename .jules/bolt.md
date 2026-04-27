# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2026-04-27 - FaissVectorStore Optimization
**Learning:** Local vector search performance is often bottlenecked by metadata retrieval (N+1 query problem) and O(N) duplicate checks during ingestion. Batching SQL queries and using set-based lookups can reduce search latency by ~50% and ingestion overhead significantly.
**Action:** Use batch SQL queries (IN clause) for metadata retrieval in vector stores and prefer sets for unique identifier tracking.
