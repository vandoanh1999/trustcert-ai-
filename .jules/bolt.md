## 2025-05-14 - [In-memory Caching for Reputation DB]
**Learning:** Repetitive disk I/O and JSON parsing for small, frequently accessed state files (like reputation scores) can significantly degrade system performance, especially during high-frequency feedback loops. In a single-process environment, a global singleton cache is a simple yet effective way to eliminate redundant reads.
**Action:** Always check if a frequently accessed JSON 'database' can be cached in memory to reduce I/O overhead.
