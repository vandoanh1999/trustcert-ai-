## 2025-05-15 - Improving expert selection UX
**Learning:** Using technical file paths in multiselect widgets is confusing for non-technical users. Emojis and human-readable aliases improve clarity.
**Action:** Always use an `EXPERT_MAP` and the `format_func` parameter in `st.multiselect` to present friendly names.

## 2025-05-15 - Enhancing feedback loops
**Learning:** Immediate visual confirmation like `st.toast` paired with a state reset (`st.rerun`) provides a satisfying closure to the feedback interaction.
**Action:** Use `st.toast` and `st.rerun` for submission-like actions in Streamlit.
