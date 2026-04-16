# Changelog

## 2026-04-16 (py_app)
- Added `Rig Setup` and `Theory` tab split.
- Added scale-aware CAGED neck rendering and expanded scale selector.
- Improved note/fret legibility on the theory neck.
- Added new readability themes (`Prism`, `Brown Sound`, `Paisley Prairie`).
- Standardized feedback form control sizing.

## 2026-04-16 (py_app_modular)
- Created modular directories: `data`, `functions`, `ui`, `automation`, `documentation`, `.git-agent`.
- Added agent contracts (`AGENTS.md`) in each operational directory.
- Moved theme definitions to `ui/theme_presets.py`.
- Moved theory-scale datasets to `data/theory_data.py` + JSON files.
- Added reusable runtime helpers in `functions/runtime_helpers.py`.
- Added automation scripts for macOS and Windows packaging.
