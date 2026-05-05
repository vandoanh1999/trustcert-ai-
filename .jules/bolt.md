# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Vector Store N+1 and O(N) Lookups
**Learning:** O(N) list lookups for duplicate checks and N+1 SQL queries during vector metadata retrieval are common bottlenecks in local vector stores like `FaissVectorStore`. Using an in-memory set for ID tracking (O(1) vs O(N)) and batching SQL metadata retrieval with an `IN` clause can significantly reduce latency (observed ~2x speedup for search with 10k vectors).
**Action:** Always use sets for membership testing of unique identifiers and batch database read operations using `IN` clauses to avoid the N+1 query pattern in storage layers.
