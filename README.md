# Pedal Architect (py_app)

Desktop PyQt5 edition of Pedal Architect for offline rig building and tone recommendations.

## Modular Branch Layout (`py_app_modular`)

- `data/`: research-backed datasets and theory JSON consumed by runtime.
- `functions/`: reusable runtime logic helpers.
- `ui/`: theme presets and visual-system configuration.
- `assets/`: static images and media.
- `automation/`: build scripts for macOS and Windows packaging.
- `documentation/`: operational docs, changelog, diagrams, and sources.
- `.git-agent/`: git workflow/bug tracking contract.
- Root `AGENTS.md`: orchestrates all scoped agents.

## What this branch includes

- `pyqt_app.py` with drag/drop pedal bank -> signal chain + reorder support.
- `Optimize For Me` chain optimizer with full permutation search for selected pedals.
- Genre presets including `Hip Hop`.
- Guitar mode + guitar profile controls.
- Amp model selection (`Auto`, Orange, Marshall, Fender Acoustic, Twin, Vox, Mesa).
- `Builder`, `Rig Setup`, `Theory`, and `Feedback` tabs.
- Persistent local state in `.pedal_architect_py_state.json`.
- Adjustable UI `Font Size` preset dropdown (`Small`, `Medium`, `Large`, `XL`) with persisted selection.
- Resizable split-panel layout so builder/settings columns scale with the window.
- Drag pedals from bank to active chain and drag active pedals back to bank to remove.
- Visual board canvas with draggable pedal graphics, guitar image node, and amp node.
- Pedal jack orientation is fixed: input on the right, output on the left.
- Guitar-to-pedal-to-amp cabling is explicit; only the connected path from guitar into amp is used for final recommendations.
- Pedal cards include `x` remove and side `~` disconnect buttons for quick edits.
- `Clean Up Layout` arranges connected pedals in a right-to-left horizontal signal row first, then wraps.
- Color scheme presets: `Dark`, `Light`, `Sunset`, `Ocean`, `Prism (Floyd)`, `Brown Sound (VH)`, and `Paisley Prairie`.
- Global top controls (including `Style`) stay visible while switching tabs.
- Amp node uses brand-adjacent color treatment per selected amp model.
- Rig Setup tab contains pedal settings cards (wrap every 5), Guitar/Amp/Justification columns, and Rig Summary.
- Theory tab contains Circle of Fifths + selectable Nashville chart + key-aware CAGED scale neck visual.
- Theory tab scale chart now supports multiple scales (minor/major pentatonic, minor blues, major scale, natural minor, mixolydian).
- Additional theory helpers include cadence mapping (`I-IV-V`, `ii-V-I`, `vi-IV-I-V`) and relative-minor guidance.
- Feedback tab sends JSON payloads to a configurable webhook with persistent anti-spam rate limiting.
- Donate flow supports PayPal, Venmo, and Zelle from `pyqt_app_config.json`.

## Run

```bash
python3 -m pip install -r requirements-pyqt.txt
python3 pyqt_app.py
```

Configure feedback/donate values in `pyqt_app_config.json` before building/distributing.

## Build Contained App

```bash
./build_py_app.sh
```

Build behavior:

- Backs up previous executable artifacts into `backups/executable_backup_<timestamp>/`
- Writes the new executable next to `pyqt_app.py`:
  - `PedalArchitect.app`

## Backup Naming

Backups use:

- `<project_name>_<branch>_<YYYY-MM-DD_HHMM>`

Example:

- `pedal_config_py_app_2026-04-16_1038`

## Branch note

- `index.html` is not used in this branch.
- The web implementation lives on the `web_app` branch.
