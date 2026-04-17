# Changelog

## 2026-04-16 (dealers_choice web-first implementation)
- Implemented the deployment decision by migrating this branch to the plain HTML/CSS/JavaScript app stack.
- Imported canonical web runtime files from `web_app` branch:
  - `index.html`, `styles.css`, `gate.js`, `app.js`, `data/config.js`, `data/access.js`, `SOURCES.md`.
- Removed PyQt-only tracked runtime/build files and modules (`pyqt_app.py`, `requirements-pyqt.txt`, `build_py_app.sh`, `functions/`, `ui/`, and Python data helpers no longer used by web runtime).
- Removed tracked pedal source-collage/reference image files and unused generated pedal PNG assets not used by web render path.
- Preserved and updated documentation to remain web-accurate:
  - `documentation/HOW_IT_WORKS.md`
  - `documentation/FUNCTIONAL_DIAGRAM.md`
  - `documentation/SOURCES.md`
- Updated `.gitignore` to enforce nested `AGENTS.md` sensitivity and keep secret directories ignored.

## 2026-04-16 (dealers_choice deployment decision)
- Added a drill-sergeant efficiency contract for local root/research/git/documentation agents (local `AGENTS.md`, intentionally gitignored).
- Completed a deployment-method comparison across:
  - Plain HTML/CSS/JS (+ optional PWA install)
  - PyQt + PyInstaller
  - Electron
  - Tauri
  - Wails (Go + webview)
- Decision matrix used (5 = best):
  - HTML/CSS/JS: user-open friction `5`, build friction `5`, offline fit `5`, maintenance simplicity `5`.
  - Tauri: user-open friction `4`, build friction `3`, offline fit `5`, maintenance simplicity `3`.
  - Wails: user-open friction `4`, build friction `3`, offline fit `5`, maintenance simplicity `3`.
  - Electron: user-open friction `4`, build friction `2`, offline fit `5`, maintenance simplicity `3`.
  - PyQt + PyInstaller: user-open friction `4`, build friction `2`, offline fit `5`, maintenance simplicity `2`.
- Chosen primary recreation stack for this branch direction: **Plain HTML/CSS/JavaScript (web-first, offline-capable, optional PWA install)**.
- Decision rationale:
  - Lowest end-user friction: open directly in browser without runtime bootstrap.
  - Lowest maintainer friction: no mandatory compile/package loop for core feature work.
  - Native support for required interactions: browser drag/drop API and persistent local storage.
  - Optional app-like install path via PWA for users who prefer launcher-style access.
  - Desktop wrappers remain optional, not required, which keeps deployment simpler than Rust/Go/Node toolchain-first stacks.
- Trimmed tracked repository payload by removing unused pedal source-collage artifacts from runtime assets.

## 2026-04-16 (py_app)
- Added `Rig Setup` and `Theory` tab split.
- Added scale-aware CAGED neck rendering and expanded scale selector.
- Improved note/fret legibility on the theory neck.
- Added new readability themes (`Prism`, `Brown Sound`, `Paisley Prairie`).
- Standardized feedback form control sizing.

## 2026-04-16 (py_app_modular)
- Created modular directories: `data`, `functions`, `ui`, `automation`, `documentation`, `.git-agent`.
- Added local scoped `AGENTS.md` contracts in each operational directory.
- Moved theme definitions to `ui/theme_presets.py`.
- Moved theory-scale datasets to `data/theory_data.py` + JSON files.
- Added reusable runtime helpers in `functions/runtime_helpers.py`.
- Added automation scripts for macOS and Windows packaging.

## 2026-04-16 (py_app_modular hardening + research refresh)
- Removed all tracked sensitive manifest files and tracked config files from source control.
- Switched back to local-only `AGENTS.md` orchestration files and removed `ROLE.md`/`OPERATIONS.md` artifacts.
- Hardened `.gitignore` to block sensitive manifest and config-file patterns.
- Added `automation/check_sensitive_files.sh` and updated git role policy to run it before push.
- Updated runtime config loading to prioritize ignored local config paths (`.secrets/pyqt_app_config.json`) and optional env override.
- Removed bundled config inclusion from `PedalArchitect.spec`.
- Refined pedal-order optimizer and added order-dependent setting adaptation rules (SD-1/DS-1 stacking, dual-EQ staging, modulation/time placement, amp gain trim by drive count).
- Refreshed pedal-order/tone research notes and source citations.
- Added new `Pedals` tab with left selector, center pedal visual, and right-side detailed pedal guide (including RC-30 deep workflow guidance).
