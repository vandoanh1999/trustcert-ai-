## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2026-06-27 - [Streamlit State Reset Callback]
**Learning:** In Streamlit, modifying a widget's session state (e.g., clearing a text area) directly in the script body after the widget has been rendered causes a crash. Using an `on_click` callback ensures state changes happen before the next render cycle, providing a stable way to implement "Clear" functionality.
**Action:** Always use callbacks for programmatic state resets of interactive widgets to maintain UI stability.
