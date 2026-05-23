# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-23 - FVS Optimization: Batched SQL and O(1) Checks
**Learning:** Sequential SQLite queries for vector metadata during searches create an N+1 query bottleneck, especially when top_k is large. Additionally, checking for duplicate vector IDs using a list scan is O(N), which slows down ingestion as the database grows.
**Action:** Use a single SQL "IN" query to fetch all metadata at once and maintain a set of vector IDs for O(1) duplicate checks. This combined optimization can improve search performance by over 100% and ensure constant-time ingestion overhead.
