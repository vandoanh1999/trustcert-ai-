## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2026-05-08 - [Dynamic Feedback & Conversational UI]
**Learning:** Using `st.chat_message` with custom avatars and providing real-time sentiment feedback (emojis/labels) on sliders makes AI interactions feel more human-centric and less like a technical form. Also, a small delay before `st.rerun()` preserves toast visibility.
**Action:** Transition static output displays to conversational components and always provide immediate visual feedback for subjective user inputs like ratings.
