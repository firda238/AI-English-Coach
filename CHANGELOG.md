# Changelog

## 2026-06-06

### Updated

- Reworked the Streamlit practice screen into a fixed-height three-column coaching terminal inspired by AI-Trader and macOS glass surfaces.
- Polished the left training rail with compact navigation, scrollable controls, smaller typography, and a clearer collapsed state.
- Refined the center chat workspace so the page itself does not scroll; conversation history remains the primary scrollable area.
- Consolidated the right analysis column into a focused learning review panel with segmented views for correction, scoring, and suggestions.
- Moved the light/dark appearance switch to the top-right chrome area and kept the visual system in a restrained graphite/silver palette.
- Preserved the existing multi-round dialogue, API/local fallback, voice transcription, scoring, history, error book, and report export flows.
- Updated the main frontend screenshot at `outputs/screenshot_final.png`.

### Verified

- `python -m py_compile app.py ui_components.py storage.py`
- `python -m pytest -q`
- `python scripts/smoke_test.py`
- `python scripts/verify_delivery.py`
- Browser check: 1280x720 practice page has no page-level scroll, with internal chat scrolling retained.
