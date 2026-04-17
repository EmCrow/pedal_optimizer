# Changelog

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
