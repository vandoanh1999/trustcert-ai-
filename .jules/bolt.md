## 2025-05-15 - Parallelizing P2P Operations
**Learning:** Sequential network loops in P2P gossip protocols (broadcast/query) create a performance bottleneck of O(N*L), where N is the number of peers and L is the latency. Using `asyncio.gather` with proper error handling (safe wrappers) reduces this to O(L).
**Action:** Always look for sequential I/O loops in networking or storage modules and parallelize them using `asyncio.gather` or similar constructs, ensuring each individual operation is wrapped in a try-except block to prevent a single failure from cancelling the entire batch.
