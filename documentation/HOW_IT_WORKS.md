# How Pedal Architect Works

## Architecture
- Runtime stack: plain `HTML + CSS + JavaScript` (no framework, offline-first).
- Entry point: `index.html`.
- Unlock gate: `gate.js` validates hostname + passkey from `data/access.js` before loading `app.js`.
- Core tone logic and UI behavior: `app.js`.
- Embedded offline rule data: `data/config.js`.

## Runtime Flow
1. Browser loads `index.html`, `styles.css`, `data/config.js`, `data/access.js`, and `gate.js`.
2. User unlocks with hostname + passkey; `gate.js` validates using Web Crypto PBKDF2 checks.
3. After successful unlock, `gate.js` loads `app.js`.
4. `app.js` initializes selectors (genre, guitar type/profile, amp model), pedal bank, and wrapped chain builder.
5. Drag/drop + reorder updates chain state and recomputes recommendations.
6. Recommendation engine applies:
   - genre preset baseline
   - order-dependent chain deltas
   - guitar profile layer
   - amp profile layer
7. UI renders:
   - pedal settings
   - guitar settings
   - amp settings
   - justification notes
   - bottom rig summary bullets
8. `Optimize For Me` runs permutation search and selects highest chain score for active pedals.
9. State persists in browser `localStorage` (`pedal_architect_state_v4`) for offline reuse.

## Deployment Model
- Simple run: open `index.html`.
- Optional app-like install path: PWA-capable browsers can install the app shell experience.
- No mandatory build step required for core use.
