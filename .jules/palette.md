## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2025-07-05 - [Conversational AI Interaction]
**Learning:** Wrapping AI-generated responses in a dedicated chat-style message block (with a custom avatar) significantly increases the "personality" of the interface and makes the interaction feel more like a dialogue rather than a cold API output.
**Action:** Use Streamlit's `st.chat_message` or equivalent conversational components for any generative AI outputs to improve user immersion.
