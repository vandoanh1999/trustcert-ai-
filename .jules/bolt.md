# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Vector Store Optimization
**Learning:** Transitioning from list-based duplicate checks to set-based lookups reduces latency from O(N) to O(1). Additionally, batching SQLite metadata retrieval with an IN clause instead of sequential queries significantly reduces overhead during vector searches, especially as the number of results (top_k) increases.
**Action:** Always use sets for membership tests and prefer batch SQL queries for retrieving multiple rows by primary key to minimize I/O and connection overhead.
