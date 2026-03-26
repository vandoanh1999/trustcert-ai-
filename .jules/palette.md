## 2025-05-15 - Streamlit Status and Toasts
**Learning:** For multi-step asynchronous processes (like model inference simulations), `st.status` provides a significantly better UX than a basic `st.spinner` by allowing granular, informative updates. Similarly, `st.toast` is superior to `st.success` for transient feedback as it doesn't shift the page layout.
**Action:** Use `st.status` for any process involving more than one logical step and `st.toast` for non-critical success notifications.

## 2025-05-15 - Session Management in Streamlit
**Learning:** Users often need a quick way to "start over" in interactive simulations. A dedicated "Reset Session" button in the sidebar that clears `st.session_state` and calls `st.rerun()` is a highly effective micro-UX pattern.
**Action:** Always include a sidebar reset button in complex interactive Streamlit applications.
