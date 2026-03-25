## 2025-05-14 - [P2P Parallelization]
**Learning:** Sequential network requests in a P2P gossip protocol create a major latency bottleneck ((N \times \text{latency})$). Using `asyncio.gather` with `return_exceptions=True` reduces this to (\max(\text{latency}))$ while remaining resilient to individual node failures.
**Action:** Always check for sequential `await` loops in network or I/O bound code and parallelize them when order doesn't matter.
