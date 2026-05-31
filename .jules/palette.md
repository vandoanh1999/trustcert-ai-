## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2025-05-31 - [Streamlit UX Toolkits]
**Learning:** Using `st.chat_message` for AI responses and `st.toast` for ephemeral success notifications significantly improves the perceived "polish" of a Streamlit app. Additionally, when using `help` tooltips, Playwright locators must be scoped by role (e.g., `get_by_role("textbox", name=...)`) to avoid "strict mode" collisions with the generated help button.
**Action:** Default to `st.chat_message` for LLM outputs and use scoped locators in frontend verification scripts.
