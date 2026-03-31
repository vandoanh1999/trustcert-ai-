## 2025-03-31 - Parallelizing P2P Gossip and Queries
**Learning:** Sequential `await` in loops over network operations (like P2P broadcasts or queries) creates a performance bottleneck that scales linearly with the number of peers. Using `asyncio.gather` reduces this to O(1) relative to peer count (plus overhead), significantly improving network responsiveness.
**Action:** Always check for serial I/O in gossip or discovery protocols and use `asyncio.gather` with proper exception wrapping to ensure parallel execution and fault tolerance.
