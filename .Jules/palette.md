# Palette's Journal - UX & Accessibility Learnings

## 2025-05-15 - [Improving Output Portability]
**Learning:** Using `st.text_area` with `disabled=True` prevents users from easily selecting and copying text in some browsers and doesn't provide a "one-click" copy experience. `st.code` in Streamlit provides a built-in "Copy to Clipboard" button and preserves formatting.
**Action:** Prefer `st.code` for displaying model-generated outputs that users might want to copy.
