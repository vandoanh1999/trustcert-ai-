## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2026-06-11 - [Conversational AI Responses in Streamlit]
**Learning:** Embedding `st.code` blocks within `st.chat_message` containers in Streamlit provides a professional conversational persona while preserving built-in "Copy to clipboard" functionality. This makes manual "(Click to copy)" text labels redundant and reduces visual noise.
**Action:** Use chat containers for AI-generated content and rely on native component features for utility actions like copying.
