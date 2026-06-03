## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2025-05-16 - [Streamlit Tooltip Disambiguation]
**Learning:** Adding 'help' tooltips to Streamlit widgets creates an additional button element with the same ARIA label as the widget, causing Playwright 'strict mode violation' errors when using 'get_by_label'.
**Action:** Use 'page.get_by_role' (e.g., 'textbox', 'button') to disambiguate interactive widgets from their associated help tooltips in automation scripts.
