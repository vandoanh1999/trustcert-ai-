# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-20 - Batched Metadata Retrieval in Vector Stores
**Learning:** Sequential database queries in a vector search loop (N+1 query problem) create a significant latency bottleneck as top_k increases. Batching these lookups into a single SQL `IN` query reduces round-trip overhead and improves search performance by over 60% (2.6x speedup in this codebase).
**Action:** Always profile vector search and RAG retrieval paths for N+1 query patterns. Use batched lookups and manual index-to-result mapping to maintain similarity ranking.
