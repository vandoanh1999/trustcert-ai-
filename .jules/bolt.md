# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2026-06-03 - SQLite N+1 Query Fix in Vector Search
**Learning:** Sequential metadata retrieval for vector search results creates a linear bottleneck (O(K)) in the SQLite layer. Using a single batched 'WHERE idx IN (...)' query reduces this to O(1) overhead, resulting in a ~3.5x throughput improvement (from ~450 to ~1650 searches/s) for top_k=100.
**Action:** Always batch database lookups when processing results from external indices (like FAISS or Lucene) to minimize I/O round-trips.
