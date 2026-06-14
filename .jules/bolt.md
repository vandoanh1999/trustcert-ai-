# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-06-14 - Vector Store O(N) Duplicate Checks & N+1 Queries
**Learning:** In storage layers like `FaissVectorStore`, using a list for membership checks (`vec_id in self.vector_ids`) leads to O(N) latency during ingestion. Additionally, retrieving metadata for search results one-by-one creates an N+1 query problem, bottlenecking the system on database roundtrips.
**Action:** Use sets for O(1) membership validation and implement batched SQLite `IN` queries to retrieve all metadata in a single roundtrip, ensuring throughput scales effectively with data volume and `top_k` values.
