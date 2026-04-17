# How Pedal Architect Works

## Runtime Flow
1. App boots and loads local state (`.pedal_architect_py_state.json`).
2. UI builds tabs (`Builder`, `Pedals`, `Rig Setup`, `Theory`, `Feedback`).
3. User selects genre/guitar/amp/theme and builds a connected signal path.
4. Recommendation engine computes pedal, guitar, and amp settings from:
   - genre presets
   - connected pedal order
   - guitar type/profile
   - amp model profile
5. `Rig Setup` renders practical settings and justification text.
6. `Theory` maps selected key + scale + CAGED shape onto a guitar neck.
7. Feedback tab can submit structured payloads via configurable webhook.
8. Pedals tab provides per-pedal visual and configuration deep dives, including RC-30 workflow guidance.

## Data Boundaries
- `data/`: theory and research-backed JSON datasets consumed by runtime.
- `functions/`: runtime utility functions and behavior helpers.
- `ui/`: theme definitions and visual-system configuration.
- `assets/`: static visual assets.
- `automation/`: build scripts and platform packaging entry points.

## Build Output
- Local build script produces `PedalArchitect.app` in repo root.
- Previous artifacts are backed up into `backups/executable_backup_*`.

## Sensitive Local Config
- Runtime defaults are embedded in `pyqt_app.py`.
- Optional feedback/donate overrides should live in ignored local paths:
  - `.secrets/pyqt_app_config.json` (preferred)
  - `PEDAL_ARCHITECT_CONFIG` environment variable path
