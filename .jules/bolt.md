## 2025-05-21 - Disk I/O Bottleneck in Reputation Updates
**Learning:** Frequent small writes and repeated reads of the same JSON file (e.g., in reputation updates) create significant I/O bottlenecks. In-memory caching provides a massive speedup for reads, though synchronous writes remain a limiting factor.
**Action:** Implement in-memory singleton caches for `aurora_reputation.json` and `aurora_vc_store.json` to eliminate redundant disk reads.
