# Pedal Architect (py_app)

Desktop PyQt5 edition of Pedal Architect for offline rig building and tone recommendations.

## What this branch includes

- `pyqt_app.py` with drag/drop pedal bank -> signal chain + reorder support.
- `Optimize For Me` chain optimizer with full permutation search for selected pedals.
- Genre presets including `Hip Hop`.
- Guitar mode + guitar profile controls.
- Amp model selection (`Auto`, Orange, Marshall, Fender Acoustic, Twin, Vox, Mesa).
- `Builder`, `Rig Settings`, and `Rig Summary` tabs.
- Persistent local state in `.pedal_architect_py_state.json`.
- Adjustable UI `Font Size` preset dropdown (`Small`, `Medium`, `Large`, `XL`) with persisted selection.
- Resizable split-panel layout so builder/settings columns scale with the window.
- Drag pedals from bank to active chain and drag active pedals back to bank to remove.
- Visual board canvas with draggable pedal graphics, guitar image node, and amp node.
- Pedal jack orientation is fixed: input on the right, output on the left.
- Guitar-to-pedal-to-amp cabling is explicit; only the connected path from guitar into amp is used for final recommendations.
- Pedal cards include `x` remove and side `~` disconnect buttons for quick edits.
- `Clean Up Layout` arranges connected pedals in a right-to-left horizontal signal row first, then wraps.
- Color scheme presets: `Dark`, `Light`, `Sunset`, and `Ocean`.
- Global top controls (including `Style`) stay visible while switching tabs.
- Amp node uses brand-adjacent color treatment per selected amp model.
- Rig Settings uses bordered pedal cards (wrap every 5) plus a dedicated second row for guitar/amp/justification.
- Rig Summary includes a Circle of Fifths (highlighted style chords) and a Nashville number chart.

## Run

```bash
python3 -m pip install -r requirements-pyqt.txt
python3 pyqt_app.py
```

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
