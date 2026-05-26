## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2025-05-20 - [Streamlit Feedback Patterns]
**Learning:** In Streamlit, when implementing non-intrusive feedback like `st.toast` followed by a state reset (`st.rerun()`), it's critical to ensure that error states are still explicitly handled. Silent failures in the background wrapper can lead to a confusing UX where the user expects an update that never happens.
**Action:** Return a `(success, error_message)` tuple from backend-calling helpers to allow the UI to choose between a success toast and an error dialog.
