## 2025-05-15 - [P2P Parallelization]
**Learning:** Sequential network operations (broadcast/query) in a P2P network create O(N) latency bottlenecks where N is the number of peers. Using `asyncio.gather` reduces this to O(1) plus constant overhead, significantly improving responsiveness in large networks.
**Action:** Always prefer `asyncio.gather` with `return_exceptions=True` for peer-to-peer communication to avoid blocking the entire operation on a single slow or dead peer.
