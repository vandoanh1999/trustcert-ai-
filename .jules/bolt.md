## 2025-04-16 - Concurrent P2P Communication
**Learning:** Sequential network calls in P2P gossip loops (broadcast/query) create a linear latency bottleneck $O(N \times L)$ that severely limits network scalability. Using `asyncio.gather` with `return_exceptions=True` for broadcasts and default behavior for queries allows for $O(L)$ latency, providing a ~10x speedup in a 10-node cluster.
**Action:** Always prefer `asyncio.gather` for outgoing network requests to multiple peers in the P2P layer to ensure the network remains responsive as it grows.
