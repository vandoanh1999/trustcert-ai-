## 2025-05-15 - Parallelizing P2P Gossip
**Learning:** Sequential network I/O in GossipP2P (broadcast/query) creates a bottleneck that scales linearly with the number of peers. Parallelizing these operations with `asyncio.gather` reduces latency from O(N*L) to O(L), achieving ~90% speedup in a 10-peer simulation.
**Action:** Always check for sequential await loops involving network or disk I/O and consider `asyncio.gather` with `return_exceptions=True` for robust concurrency.
