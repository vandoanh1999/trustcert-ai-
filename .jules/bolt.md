## 2025-05-15 - [P2P Parallelization]
**Learning:** Sequential network operations in a P2P gossip protocol create an O(N) bottleneck that scales poorly with peer count and latency. Using asyncio.gather with return_exceptions=True allows for O(1) broadcast/query times while maintaining robustness against individual peer failures.
**Action:** Always check for loops containing awaitable network calls and consider parallelization with proper error handling (e.g., return_exceptions=True or safe wrappers).
