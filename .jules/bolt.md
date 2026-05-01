# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - O(1) Duplicate Checks and Batch SQL in Vector Store
**Learning:** O(N) list lookups for duplicate checks during bulk vector ingestion create an O(N^2) bottleneck. Switching to a set reduces this to O(N). Additionally, fetching metadata for search results in a single SQL 'IN' query instead of N individual queries reduces database latency significantly.
**Action:** Use sets for ID tracking and batch database queries whenever processing multiple records to maintain performance as data scales.
