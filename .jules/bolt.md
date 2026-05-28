# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched Persistence in FVS
**Learning:** In the `FaissVectorStore`, synchronous SQLite commits on every insertion and N+1 query patterns in search create massive I/O bottlenecks. Ingestion speed was increased ~13x (394 -> 5270 vectors/sec) by batching commits every 100 vectors, and search speed improved ~43% by batching metadata retrieval into a single SQL `IN` query.
**Action:** Always batch I/O operations (commits, queries) in storage layers. Use a set for duplicate checks to maintain O(1) performance as the dataset grows.
