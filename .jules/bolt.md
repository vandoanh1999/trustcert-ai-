## 2025-05-15 - [File-based I/O Bottleneck in Reputation/VC Stores]
**Learning:** Frequent small writes and repeated reads of the same JSON file (e.g., in `update_reputation_with_feedback` which reads twice and writes once per update) cause a significant performance bottleneck due to disk I/O and JSON parsing overhead. In-memory caching can reduce this overhead by orders of magnitude for read operations.
**Action:** Always consider implementing simple in-memory caching for frequently accessed file-based storage modules. Ensure the cache is updated on both reads and writes.
