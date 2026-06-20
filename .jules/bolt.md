# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Optimized FAISS Vector Store Storage
**Learning:** Metadata retrieval in vector stores often suffers from the N+1 query problem, where each search result triggers a separate database lookup. Batching these into a single SQL 'IN' query reduces overhead significantly. Additionally, linear list lookups for duplicate checks become a bottleneck as the store grows; using a mirrored hash set maintains O(1) performance.
**Action:** Use batched database queries for metadata retrieval and hash-based structures for membership checks in storage layers.
