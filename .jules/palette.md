## 2025-05-22 - [Streamlit: st.code for AI outputs]
**Learning:** For AI-generated text, using `st.code` instead of a disabled `st.text_area` provides a much better user experience. It offers better formatting, syntax highlighting (if applicable), and a built-in "Copy to Clipboard" button, which is essential for LLM interfaces.
**Action:** Always prefer `st.code` for displaying model outputs in Streamlit applications.

## 2025-05-22 - [Streamlit: Toast & Rerun for feedback flow]
**Learning:** Pairing `st.toast` with `time.sleep(1)` and `st.rerun()` provides a clean way to clear the UI state (e.g., hiding a feedback panel) while giving immediate, non-intrusive visual confirmation to the user.
**Action:** Use this pattern for action confirmations that should trigger a view reset.
