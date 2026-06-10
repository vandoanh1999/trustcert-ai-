## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2026-06-10 - [Streamlit Tooltip Collision in Automation]
**Learning:** Adding `help` tooltips to Streamlit components creates additional buttons with nearly identical ARIA labels (e.g., "Help for [Label]"), which can cause "strict mode violation" errors in Playwright when using `get_by_label`.
**Action:** When automating Streamlit UIs with tooltips, prefer `page.get_by_role('textbox', name='...')` or specific `data-testid` locators to disambiguate the actual input from its help icon.
