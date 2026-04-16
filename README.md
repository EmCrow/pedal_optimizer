# Pedal Architect

Offline-ready drag-and-drop pedalboard app for guitar tone setup.

## What it does

- Drag pedals into your signal chain and reorder them.
- Chain view wraps to multiple rows (no horizontal scrolling).
- Includes your pedals: `BOSS CS-3`, `BOSS SD-1`, `BOSS BD-2`, `BOSS DS-1`, `BOSS GE-7`, `10-band EQ`, `BOSS CH-1`, `BOSS DD-3`, and `RC-30 Loop Station`.
- Fixed amp node at the end of chain.
- Genre selector (`Metal`, `Rock`, `Classic Rock`, `Pop`, `Country`, `Blues`).
- Guitar type selector (`Electric`, `Acoustic`).
- Guitar control selector with profile-aware settings:
  - `Taylor Acoustic (ES2 Bass/Treble)`
  - `Electric 2 Knob + Toggle`
  - `Electric 4 Knob + Toggle`
- Taylor acoustic profile intentionally leaves output volume to player control for stage feedback management.
- Amp selector (`Auto`, `Orange Rockerverb MKIII`, `Marshall JCM800 2203`, `Fender Acoustic 100`, `Fender Twin Reverb`, `Vox AC30`, `Mesa/Boogie Dual Rectifier`).
- Shows recommended pedal and amp settings based on both genre and your current chain order.
- Pedal graphics update knob and slider positions to mirror current recommended settings.
- `Optimize For Me` auto-builds a recommended chain for the selected genre.
- Saves your latest setup in browser storage for offline reuse.

## Run

1. Open `index.html` in a browser.
2. No install step and no internet required after files are local.

## Data notes

Preset behavior is based on embedded rule data in `data/config.js` so recommendations work offline.

The recommendation logic combines:
- Official control layouts for CS-3 / SD-1 / BD-2 / DS-1 / GE-7 / CH-1 / DD-3 / RC-30.
- Official pedal-order guidance from BOSS.
- Official EQ placement guidance from BOSS and 10-band frequency structure from MXR M108S documentation.
- Practical genre voicing heuristics (inferred from those references).

## Files

- `index.html` - layout and controls
- `styles.css` - UI theme, responsive layout, pedal visuals
- `app.js` - drag/drop logic, recommendation engine, offline save
- `data/config.js` - pedal library, genre presets, amp models, guitar profiles, chain-order rules
