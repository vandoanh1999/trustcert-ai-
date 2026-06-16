# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2026-06-16 - FaissVectorStore SQL Batching and Set Lookup
**Learning:** SQL N+1 metadata retrieval in vector search methods becomes a major bottleneck as top_k increases. Batching these into a single "WHERE idx IN (...)" query provides significant throughput gains (~2.5x). Additionally, using a list for membership checks (duplicate detection) scales poorly (O(N)); maintaining a parallel set for O(1) checks is essential for high-ingestion performance.
**Action:** Always batch database metadata lookups for search results and use sets for high-frequency membership checks in storage layers.
