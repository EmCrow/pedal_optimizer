# Changelog

## 2026-04-17 (installer compatibility hardening)
- Added dual Qt runtime support in `pyqt_app.py`: prefer `PyQt5` when available, then fall back to `PySide6`.
- Added compatibility wrappers for drag/modal execution so the same code path works across `PyQt5` and `PySide6`.
- Updated `requirements-pyqt.txt` to select Qt binding by Python version (`PyQt5` for older Python, `PySide6` for newer Python).
- Hardened `build_app.py` with:
  - Python/macOS preflight checks.
  - `pip/setuptools/wheel` bootstrap upgrade.
  - fallback dependency install sets when primary requirements resolution fails.
  - explicit legacy macOS guidance for Python version constraints.

## 2026-04-17 (py_app_modular build simplification)
- Added a single cross-platform build entrypoint: `build_app.py`.
- Build flow now bootstraps its own temporary virtualenv, installs `requirements-pyqt.txt`, packages via PyInstaller, and cleans temporary files automatically.
- Builder now bundles `assets/` and `data/` directly from CLI flags (no external `.spec` dependency).
- Removed redundant build wrappers: `build_py_app.sh`, `automation/build_macos.sh`, `automation/build_windows.ps1`.
- Updated build docs to use the one-command Python workflow.

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
