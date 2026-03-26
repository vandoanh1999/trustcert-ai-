## 2025-05-15 - [P2P Parallelization with asyncio.gather]
**Learning:** Sequential network operations (broadcast/query) in a P2P network create a latency bottleneck that scales linearly with the number of peers. Using `asyncio.gather` with `return_exceptions=True` allows concurrent execution, reducing total latency to approximately the time of the slowest single request.
**Action:** Always check for `for` loops containing `await` in I/O-bound code paths, especially for network-distributed systems, and consider parallelizing with `asyncio.gather`.
