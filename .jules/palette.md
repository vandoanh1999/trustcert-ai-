## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2025-05-16 - [Horizontal Action Grouping]
**Learning:** In search or query-heavy interfaces, grouping 'Action' and 'Reset' buttons horizontally with balanced visual weight (e.g., using `st.columns`) provides a more intuitive and desktop-standard experience compared to stacked vertical buttons.
**Action:** Use horizontal columns for primary and secondary actions (like Query/Clear) and ensure `use_container_width=True` for a cohesive look.
