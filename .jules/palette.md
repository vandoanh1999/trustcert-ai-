## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2026-05-23 - [Conversational UI vs. Code Blocks]
**Learning:** In Streamlit, replacing `st.code` with `st.chat_message` for AI responses removes the built-in 'Click to copy' button; however, the improved readability (Markdown support) and the visual persona (e.g., using '🌌' avatar) create a much more engaging and human-centric experience for non-technical users.
**Action:** Prioritize conversational components for assistant responses while acknowledging the trade-off in raw utility for copy-pasting.
