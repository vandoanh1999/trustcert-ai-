# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-06-08 - Optimized Vector Storage Metadata Retrieval and Duplicate Checks
**Learning:** SQL N+1 query patterns in high-frequency search paths (like vector stores) drastically reduce throughput. Linear lookups for duplicate detection in write-heavy stores become a bottleneck as the dataset grows (O(N)).
**Action:** Use SQL `IN` clauses for batched metadata retrieval and auxiliary `set` data structures for O(1) membership checks to maintain constant-time performance.
