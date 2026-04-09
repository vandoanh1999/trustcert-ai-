## 2026-04-09 - Humanizing Technical Identifiers in Multi-Expert Selection
**Learning:** Technical identifiers, such as file paths or model adapter names, create a high cognitive load for non-technical users in selection widgets. Using a mapping layer to provide friendly aliases with visual cues (emojis) improves both delight and usability.
**Action:** Implement a UI-agnostic mapping layer (like `EXPERT_MAP`) whenever backend identifiers need to be exposed to the user interface, ensuring the friendly names are used for display while preserving technical accuracy for API calls.
