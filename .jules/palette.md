# Palette's UX Learning Journal - Genesis Core V8

## 2025-05-24 - Streamlit Feedback & Hierarchy
**Learning:** In Streamlit, users benefit from interactive feedback during long-running tasks. Replacing a generic `st.spinner` with `st.status` allows for granular reporting of process stages (e.g., expert identification, P2P routing), which reduces perceived wait time.
**Action:** Use `st.status` for multi-stage async processes and `st.code` for primary content output to provide built-in accessibility features like 'Copy to Clipboard'.
