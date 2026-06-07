## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2025-06-07 - [Multi-Layered Guidance & Status Feedback]
**Learning:** In interactive AI applications, using `st.status` for granular feedback during long-running tasks provides much better UX than a simple spinner. Combining this with `placeholder` and `help` tooltips creates "multi-layered guidance" that reduces user anxiety during complex operations.
**Action:** Use `st.status` for multi-step backend processes and ensure all primary inputs have both a placeholder example and a help tooltip.
