## 2025-02-14 - Reputation system in-memory caching
**Learning:** Frequent small writes and repeated reads of the same JSON file (e.g., in reputation updates) create significant I/O bottlenecks. In-memory caching provides a massive speedup for reads (up to 90x), while synchronous writes remain the primary limiting factor for performance in this architecture.
**Action:** Always implement a simple in-memory cache for JSON-backed state that is frequently accessed. Consider asynchronous or batched writes for even greater performance gains in future updates.
