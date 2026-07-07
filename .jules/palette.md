## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2026-07-07 - [Streamlit Session State vs Default Value]
**Learning:** Initializing a widget's value in `st.session_state` while also providing a `default` argument to the widget itself (with the same `key`) triggers a warning. It's cleaner to initialize in session state and let the widget consume it.
**Action:** Initialize complex widget states in session state at the start of the app and omit the `default` parameter in the widget call.
