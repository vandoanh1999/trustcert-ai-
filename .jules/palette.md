## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2026-07-03 - [Contextual Guidance and Layout Balance]
**Learning:** In Streamlit applications, grouping related actions (like 'Query' and 'Clear') horizontally with balanced visual weight (using `use_container_width=True`) creates a more professional look. Additionally, using tooltips to explain why a button is disabled (e.g., missing input) reduces user frustration and makes the interface more accessible for screen readers.
**Action:** Group primary and secondary actions horizontally in columns, and always provide `help` tooltips on buttons that can be disabled due to missing input.
