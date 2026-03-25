## 2025-05-15 - [Reset Session Pattern in Streamlit]
**Learning:** In Streamlit, programmatically clearing input widgets (like `st.text_area`) requires a dynamic `key` that is incremented in the session state to force a widget reset. Simply clearing the value in `st.session_state` doesn't always reflect in the UI immediately for widgets.
**Action:** Use `key=f"widget_{st.session_state.widget_key}"` and increment `widget_key` during reset operations.
