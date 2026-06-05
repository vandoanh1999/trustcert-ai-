## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2025-05-16 - [Streamlit Conversational UI Pattern]
**Learning:** Wrapping AI responses in `st.chat_message` with thematic emoji avatars (like 🌌) creates a distinct assistant identity and improves conversational flow. Embedding `st.code` within these messages preserves built-in "Copy to clipboard" functionality while maintaining the UI persona.
**Action:** Use `st.chat_message` for expert/AI responses and leverage native Streamlit component features (like code block copy buttons) instead of adding manual instructions.
