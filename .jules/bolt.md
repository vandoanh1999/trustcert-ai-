## 2025-05-15 - [P2P Parallelization]
**Learning:** Sequential network operations in a P2P gossip protocol create a linear performance bottleneck as the number of peers grows. For a network with $N$ peers and an average latency $L$, sequential operations result in $O(N \times L)$ total time, while parallelizing via `asyncio.gather` reduces this to $O(L)$, assuming sufficient local bandwidth and resources.
**Action:** Always favor `asyncio.gather` for broadcasting or querying multiple remote peers in P2P systems to ensure constant-time operations relative to peer count.
