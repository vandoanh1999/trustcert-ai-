## 2025-04-01 - Parallelized P2P Network Operations

**Learning:** Sequential `await` loops for network operations (broadcasts, queries) scale linearly with the number of peers. In a decentralized network, this quickly becomes a bottleneck. Parallelizing these operations with `asyncio.gather` reduces the latency from O(N) to roughly O(1), improving responsiveness by ~75% for a typical 4-5 peer configuration.

**Action:** Always prefer `asyncio.gather` for independent network tasks like broadcasting or multi-node queries. Use `return_exceptions=True` for queries and safe wrappers for broadcasts to ensure partial network failures don't disrupt the whole operation.
