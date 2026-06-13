## 2025-05-15 - [Expert Alias Mapping]
**Learning:** Mapping technical internal paths (like expert model filepaths) to human-readable aliases in the UI significantly reduces cognitive load for non-technical users and makes the system feel more approachable.
**Action:** Always use a mapping layer between backend identifiers and frontend display labels for user-facing selection components.

## 2026-06-13 - [Conversational Context & Action Guidance]
**Learning:** Using `st.chat_message` for AI-generated content transforms technical output into a conversational flow, significantly improving user engagement. Additionally, pairing primary action buttons with conditional tooltips to explain disabled states reduces user frustration by providing immediate, actionable guidance.
**Action:** Default to `st.chat_message` for AI responses and always provide `help` tooltips on conditional buttons to explain interface restrictions.
