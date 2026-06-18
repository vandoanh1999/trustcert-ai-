## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2026-06-18 - [Conversational Branding & Non-Intrusive Feedback]
**Learning:** Utilizing `st.chat_message` with a brand-specific emoji (like 🌌) and `st.toast` instead of `st.success` transforms a technical tool into a cohesive conversational experience, reducing visual "loudness" while maintaining clear feedback.
**Action:** Prefer `st.toast` for transient confirmations and `st.chat_message` for AI-generated content to align with modern chat UX patterns.
