# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-14 - Batched SQL Metadata Retrieval
**Learning:** Fetching metadata in a loop for each vector returned by FAISS (N queries) creates a significant bottleneck due to database roundtrips and parsing overhead (N+1 query problem). Using a single `IN` query to fetch all metadata at once reduces this to O(1) database overhead, providing a ~3.3x speedup for `top_k=100`.
**Action:** When retrieving metadata for a list of identifiers from SQLite, always use a single batched `IN` query and map results back to the original order using a dictionary.
