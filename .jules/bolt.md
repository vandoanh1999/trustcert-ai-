## 2025-05-15 - [P2P Parallelization]
**Learning:** Parallelizing P2P operations with `asyncio.gather` significantly reduces latency from $O(N \times L)$ to $O(L)$, where $N$ is the peer count and $L$ is network latency. However, robust error handling with `return_exceptions=True` is critical to prevent a single peer failure from cascading and failing the entire network operation.
**Action:** Always use `asyncio.gather` with `return_exceptions=True` or a safe-wrapper for network-bound fan-out operations in distributed systems to ensure high availability and low latency.
