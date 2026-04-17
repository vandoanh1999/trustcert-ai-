## 2025-05-15 - [Form Reset Pattern in Streamlit]
**Learning:** When using `st.session_state` to store user inputs and wanting to clear them via a "Reset" button, simply clearing the session state is sometimes insufficient for certain widgets. Using a dynamic `key` (e.g., `key=f"input_{st.session_state.widget_key}"`) and incrementing that `widget_key` in the reset logic is a robust way to force-clear all widgets and ensure a clean state.
**Action:** Use a global `widget_key` in `st.session_state` to manage widget lifecycle when a full session reset is required.

## 2025-05-15 - [Multi-step feedback with st.status]
**Learning:** Users can feel anxious during long-running async operations. `st.status` provides a much better experience than a simple `st.spinner` because it allows for granular progress updates ("Selecting experts...", "Consulting Core..."), making the wait feel shorter and more transparent.
**Action:** Prefer `st.status` for any process that involves multiple logical steps or network calls.
