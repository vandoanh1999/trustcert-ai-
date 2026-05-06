# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - FaissVectorStore O(1) Checks and Batched SQL
**Learning:** O(N) list scans for duplicate checks in vector stores become a major bottleneck as the collection grows (e.g., 1.8s for 10k vectors). Using an in-memory set reduces this to O(1) (~0.014s). Additionally, N separate SQL queries for metadata retrieval during search can be consolidated into a single 'IN' query, reducing database roundtrip overhead and significantly lowering search latency (~2.3x speedup).
**Action:** Use sets for identity/membership checks and leverage SQL 'IN' clauses for batch metadata retrieval to ensure constant-time operations and minimal I/O overhead.
