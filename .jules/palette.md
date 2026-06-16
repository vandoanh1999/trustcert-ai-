## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2025-06-16 - [Proactive Interface Guidance]
**Learning:** Users are often frustrated by disabled buttons without explanation. Combining input placeholders with dynamic `help` tooltips on disabled buttons provides "multi-layered guidance" that helps users understand exactly how to proceed without trial and error.
**Action:** When a primary action button is disabled due to missing inputs, always provide a `help` tooltip explaining the specific requirement (e.g., "Select an expert to continue").
