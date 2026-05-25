## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2026-05-25 - [Conversational Utility]
**Learning:** Embedding `st.code(..., language='markdown')` within a `st.chat_message` block preserves the built-in 'Copy to clipboard' functionality while maintaining a conversational UI persona. This balances "delight" with "utility" for AI responses.
**Action:** Use `st.chat_message` with nested `st.code` for responses that users may need to extract or reuse.

## 2026-05-25 - [Ephemeral Feedback Loops]
**Learning:** The pattern of `st.toast` followed by `st.rerun()` (with a brief `time.sleep`) creates a highly responsive feedback loop for form submissions, immediately confirming the action and resetting the state for the next interaction without page-level clutter.
**Action:** Prioritize `st.toast` + `st.rerun` for quick confirmation actions like feedback or "save" events.
