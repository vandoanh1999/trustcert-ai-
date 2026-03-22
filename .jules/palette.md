## 2025-05-14 - [Streamlit UX: Reset Session & Code Formatting]
**Learning:** In Streamlit, users often feel "stuck" when a session state persists across different tasks. Adding a clear 'Reset Session' button in a sidebar, combined with `st.rerun()`, significantly improves the sense of control. For AI-generated content, `st.code` is superior to `st.text_area` as it provides a native 'Copy to Clipboard' button and better typography.
**Action:** Always include a sidebar with a 'Reset Session' button in Streamlit apps and prioritize `st.code` for model outputs.

## 2025-05-14 - [Playwright Verification for Streamlit]
**Learning:** Streamlit session state often syncs on loss of focus or specific keyboard events (like Tab or Enter). When verifying with Playwright, it's crucial to trigger these events explicitly before clicking buttons. Additionally, using `scroll_into_view_if_needed()` and large viewports ensures that dynamic Streamlit components are captured correctly in screenshots.
**Action:** Use `instruction_input.press("Tab")` and `page.set_viewport_size({"width": 1280, "height": 1200})` when testing Streamlit apps.
