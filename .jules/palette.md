## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2025-05-16 - [Multi-layered Input Guidance]
**Learning:** Combining thematic emojis in labels, detailed 'help' tooltips, and clear 'placeholder' text in Streamlit input widgets (like `st.text_area`) creates a multi-layered guidance system that minimizes cognitive load and clarifies expected user behavior.
**Action:** Use 'placeholder' and 'help' parameters for all primary user inputs to provide context without cluttering the main UI.

## 2025-05-16 - [Conversational UI Framing]
**Learning:** Framing AI responses within an `st.chat_message` component using a thematic avatar (e.g., '🌌') significantly improves the perceived "intelligence" and "personality" of the network compared to static code blocks or plain text.
**Action:** Prefer `st.chat_message` for all non-technical AI outputs to maintain a consistent conversational persona.
