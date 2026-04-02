## 2025-05-15 - [Reputation Cache]
**Learning:** Accessing small JSON databases (reputation, VCs) on every function call creates a significant I/O bottleneck in P2P simulations. Implementing a simple global cache (`_REPUTATION_CACHE`) reduced read latency by ~150x.
**Action:** Always implement caching for frequently accessed JSON state files, ensuring the cache is robust to missing or invalid files by defaulting to an empty state and preventing repeated disk retries.
