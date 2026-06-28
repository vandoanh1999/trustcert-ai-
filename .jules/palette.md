## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2026-06-28 - [Dynamic State-Based Guidance]
**Learning:** Providing specific reasons why a button is disabled (e.g., "Please enter an instruction first" vs. "Please select an expert") via tooltips significantly reduces user confusion compared to a static "disabled" state.
**Action:** Use dynamic `help` parameters on Streamlit buttons to explain prerequisite states when they are disabled.
