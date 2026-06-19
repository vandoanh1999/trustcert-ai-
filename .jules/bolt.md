# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - FaissVectorStore Optimization
**Learning:** N+1 SQL queries during vector metadata retrieval and O(N) list lookups for duplicate checks are significant bottlenecks as the store grows. Batched SQL IN queries and using a set for membership checks provide massive throughput gains.
**Action:** Always use sets for O(1) membership checks and batch database/IO operations when mapping external indices (like FAISS) back to metadata.
