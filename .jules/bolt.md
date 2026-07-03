# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched SQLite Metadata Retrieval
**Learning:** Performing individual SQLite lookups for each vector search result in a loop creates $N$ roundtrips to the database. Replacing this with a single `IN` clause query and in-memory mapping reduces search latency by ~64% (increasing throughput from ~917 to ~2566 searches/s for $k=50$). Additionally, replacing $O(N)$ list-based duplicate checks with $O(1)$ set-based checks ensures consistent performance as the vector store scales.
**Action:** Use SQL `IN` clauses for batch metadata retrieval and maintain sets for high-frequency membership checks in storage layers.
