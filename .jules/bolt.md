## 2025-05-21 - [Parallelizing P2P Gossip]
**Learning:** Sequential network operations in a decentralized P2P system lead to linear latency O(N). Parallelizing with `asyncio.gather` reduces this to O(1) (effective latency of the slowest peer). Robustness is critical; using `return_exceptions=True` or safe wrappers ensures that individual peer failures don't block the entire network activity.
**Action:** Always parallelize outbound P2P communications (broadcasts/queries) to ensure network scalability.
