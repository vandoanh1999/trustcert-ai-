# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-06-22 - Vector Store Metadata Throughput
**Learning:** Individual SQL lookups in a vector search result loop create an N+1 query bottleneck that scales poorly with `top_k`. Batching metadata retrieval using `WHERE idx IN (...)` and mapping results in-memory improved search throughput by ~3.4x. Additionally, O(N) list-based duplicate checks in the storage layer become a primary bottleneck as the database grows; a synchronized `set` provides O(1) validation and improved save/check speed by >25x.
**Action:** Always batch database lookups for search results and use hash-based structures for membership validation in local storage engines.
