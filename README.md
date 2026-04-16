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
- Visual board canvas with draggable pedal images and click-drag cable routing into amp.
- Only pedals connected by placed cables into the amp are used for final recommendations.
- Color scheme presets: `Dark`, `Light`, `Sunset`, and `Ocean`.

## Run

```bash
python3 -m pip install -r requirements-pyqt.txt
python3 pyqt_app.py
```

## Branch note

- `index.html` is not used in this branch.
- The web implementation lives on the `web_app` branch.
