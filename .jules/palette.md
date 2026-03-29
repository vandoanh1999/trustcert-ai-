## 2025-03-29 - [Expert Aliases in Multiselect]
**Learning:** Raw technical implementation details like file paths (`dummy_adapters/expert_A/adapter_model.bin`) should be hidden from the UI to avoid "leaky abstractions" and improve user trust. Descriptive aliases with icons significantly improve the "Expert Network" metaphor.
**Action:** Always map technical identifiers to friendly display names in Streamlit UI components using a dictionary/mapping pattern.
