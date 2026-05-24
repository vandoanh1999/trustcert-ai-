# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Optimized FaissVectorStore Ingestion and Search
**Learning:** Synchronous SQLite commits on every vector insertion create a massive I/O bottleneck, especially when paired with FAISS index updates. Batching metadata retrieval using SQL `IN` clauses in the search path resolves the N+1 query problem, which is critical for maintaining low latency as `top_k` increases.
**Action:** In storage layers, align database transaction boundaries with higher-level persistence intervals (like FAISS index saves) and use batched queries to fetch related metadata in a single roundtrip.
