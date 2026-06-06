# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Batched SQLite Queries and Set-based Lookups
**Learning:** SQLite's N+1 query problem significantly throttles vector search performance when fetching metadata for top-K results. Moving from iterative queries to a single `IN` clause query yields a ~2.8x speedup in search throughput (~930 to ~2600 queries/s). Additionally, using a `set` for duplicate ID checks instead of a `list` improves ingestion efficiency from O(N) to O(1).
**Action:** Always audit for N+1 query patterns in data-intensive loops and replace with batched operations. Use appropriate data structures (sets/dicts) for O(1) lookups in performance-critical paths.
