# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - In-Memory Caching for Reputation
**Learning:** Repeatedly reading and parsing a JSON database from disk for frequent lookups (e.g., node reputation checks) introduces significant I/O latency (~0.5ms per call). Implementing a global in-memory cache with a fallback to disk reduces latency by ~80x (~0.006ms per call).
**Action:** Identify frequently accessed small-to-medium sized data files and implement in-memory caching with synchronized writes to avoid redundant disk I/O.
