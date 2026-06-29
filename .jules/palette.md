## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2025-05-16 - [Action Grouping and State Reset]
**Learning:** Grouping primary and secondary actions (like 'Query' and 'Clear') horizontally using columns makes the interface more compact and balanced. Providing an explicit 'Clear' button via session state callbacks significantly improves the user experience for iterative tasks.
**Action:** Use `st.columns` for action buttons and implement `on_click` callbacks to reliably reset UI state.
