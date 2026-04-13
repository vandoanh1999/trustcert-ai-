## 2025-04-13 - Mtime-validated In-Memory Caching
**Learning:** Implementing in-memory caching for JSON-based local storage requires a validation mechanism (like file modification time) to prevent data corruption/loss in multi-process environments (e.g., Streamlit + API server).
**Action:** Always verify 'os.path.getmtime()' against a cached timestamp before returning cached data to ensure synchronization with the disk.
