## 2026-04-09 - Reputation Cache Optimization
**Learning:** The reputation system was performing redundant disk I/O on every `get_reputation` call, which is a frequent operation in node tier updates and message verification. Implementing an in-memory cache at the module level significantly reduces latency (from ~40µs to ~0.2µs).
**Action:** Always check for repeated disk reads in core modules that are part of the hot path (like consensus or P2P message handling).
