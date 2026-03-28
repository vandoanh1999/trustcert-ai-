## 2025-03-28 - [Streamlit Feedback Loop Optimization]
**Learning:** In Streamlit, using `st.status` provides a much more engaging experience for multi-step backend processes than a simple spinner. Additionally, pairing `st.toast` with a session reset/rerun allows for a clean "transactional" feel to user feedback.
**Action:** Prefer `st.status` for any process involving more than one logical step, and use `st.toast` for success confirmations that don't need to block the UI.
