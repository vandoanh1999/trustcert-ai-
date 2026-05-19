## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.
## 2026-05-19 - Enhancing Conversational UX and Playwright Robustness
**Learning:** Replacing static code blocks with the `st.chat_message` component significantly improves the conversational feel of AI interactions, aligning with user expectations for LLM interfaces. Additionally, adding `help` tooltips to Streamlit widgets causes `page.get_by_label` to fail in Playwright due to multiple elements (the input and the help icon) sharing the label.
**Action:** Prioritize conversational components for AI outputs. When testing Streamlit apps with tooltips using Playwright, use `page.get_by_role("textbox", name="...")` or similar role-based locators to target the correct element.
