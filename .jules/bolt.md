# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Vector Store N+1 and O(N) Lookups
**Learning:** In-memory list lookups for duplicate checks scale poorly (O(N)), and sequential database queries in search loops (N+1 problem) create significant I/O overhead. Using a set for membership tests and SQL `IN` clauses for batched retrieval provides massive throughput gains (~49x for duplicate checks, ~3x for search).
**Action:** Use sets for O(1) existence checks and batch database queries using `IN` or JOINs to minimize roundtrips in performance-critical paths.
