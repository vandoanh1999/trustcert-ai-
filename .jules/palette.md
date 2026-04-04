# Palette UX Journal

This journal documents critical UX and accessibility learnings for the Genesis Core V8 project.

## 2026-04-04 - [Enhanced Feedback and Expert Selection]
**Learning:** Mapping technical IDs (like file paths) to emoji-enhanced, human-readable aliases significantly improves interface clarity for non-technical users. Additionally, using modern Streamlit components like `st.feedback` provides a more natural rating experience than sliders, and it handles script reruns automatically, making manual `st.rerun()` calls redundant and potentially disruptive (causing double-refreshes).

**Action:** Always use mapping dictionaries (EXPERT_MAP) for technical identifiers in the UI. Prefer `st.feedback` over sliders for ratings, and avoid `time.sleep()` or manual `st.rerun()` immediately after widget interactions that already trigger a rerun.
