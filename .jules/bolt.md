# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - Vector Store O(1) Duplicate Checks & Batch Metadata
**Learning:** Checking for duplicates in a list of vector IDs scales linearly (O(N)), which becomes a major bottleneck during batch ingests (O(N^2) total). Using an in-memory `set` for lookups reduces this to O(1). Additionally, fetching metadata for search results sequentially (N+1 query problem) adds significant round-trip latency. A single `SQL IN` query for all result IDs is much more efficient.
**Action:** Use sets for existence checks in large collections and always batch database queries for multiple IDs.
