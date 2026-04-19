# Bolt ⚡ Performance Journal

## 2025-05-14 - Concurrent P2P Gossip
**Learning:** Sequential network calls in P2P gossip protocols scale latency linearly with the number of peers (O(N*L)). Parallelizing these calls using `asyncio.gather` reduces the bottleneck to the maximum latency of a single peer connection (O(max(L))), resulting in a ~10x speedup for a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for independent network I/O or disk I/O operations in the P2P and storage layers to minimize total execution time.

## 2025-05-15 - In-Memory Reputation Caching
**Learning:** Frequent JSON file reads (O(I/O)) for reputation lookups create a significant bottleneck in trust-heavy workflows. Implementing an in-memory cache reduced `get_reputation` latency by ~15x (from 0.044ms to 0.003ms), shifting the overhead from disk to CPU.
**Action:** Use global or singleton-based caching for JSON-backed stores that are frequently read but rarely changed. Ensure the cache is invalidated or updated on writes to maintain consistency.
