# Pedal Architect

Offline-ready drag-and-drop pedalboard app for guitar tone setup.

## What it does

- Drag pedals into your signal chain and reorder them.
- Chain view wraps to multiple rows (no horizontal scrolling).
- Includes your pedals: `BOSS CS-3`, `BOSS SD-1`, `BOSS BD-2`, `BOSS DS-1`, `BOSS GE-7`, `10-band EQ`, `BOSS CH-1`, `BOSS DD-3`, and `RC-30 Loop Station`.
- Fixed amp node at the end of chain.
- Genre selector (`Metal`, `Rock`, `Classic Rock`, `Pop`, `Country`, `Hip Hop`, `Blues`).
- Guitar type selector (`Electric`, `Acoustic`).
- Guitar control selector with profile-aware settings:
  - `Taylor Acoustic (ES2 Bass/Treble)`
  - `Electric 2 Knob + Toggle`
  - `Electric 4 Knob + Toggle`
- Taylor acoustic profile intentionally leaves output volume to player control for stage feedback management.
- Amp selector (`Auto`, `Orange Rockerverb MKIII`, `Marshall JCM800 2203`, `Fender Acoustic 100`, `Fender Twin Reverb`, `Vox AC30`, `Mesa/Boogie Dual Rectifier`).
- Shows recommended pedal and amp settings based on both genre and your current chain order.
- `Order Lab` exhaustively checks every possible pedal order for your active pedal set and recommends the best chain.
- Under the amp panel, each style includes heard-chord progressions, capo-5 shape progressions, open-shape mapping, and G-shape pentatonic fret-position solo direction.
- Pedal graphics update knob and slider positions to mirror current recommended settings.
- GE-7 and 10-band EQ placement now includes explicit on-page justification when they are adjacent or intentionally separated.
- `Optimize For Me` auto-builds a recommended chain for the selected genre.
- Saves your latest setup in browser storage for offline reuse.

## Run

1. Generate or update a device key entry (hostname + passkey):

```bash
python3 .secrets/device_keygen.py --hostname "<your-laptop-hostname>" --label "<friendly-name>"
```

2. Open `index.html` in a browser.
3. At unlock prompt, enter the same hostname and generated passkey.
4. No install step and no internet required after files are local.

## Device lock (hostname + secret key)

- `index.html` now opens to a secure unlock gate.
- Access is validated against hashed host entries in `data/access.js`.
- Optional passkey persistence is available via `Remember passkey on this laptop`.
- Per-laptop passkeys are deterministically derived from:
  - local `.secrets/device_secrets.json` master key
  - local owner key
  - target hostname
- Key generation helper is local-only and gitignored:
  - `.secrets/device_keygen.py`

Add/update an authorized laptop:

```bash
python3 .secrets/device_keygen.py --hostname "studio-mac.local" --label "Studio Mac"
```

Print only (do not update access policy):

```bash
python3 .secrets/device_keygen.py --hostname "studio-mac.local" --print-only
```

## Secure package (local-only key)

- Local passkey file: `.secrets/pedal_passkey.txt` (git-ignored).
- Encrypted binary archive output: `secure_package/*.tar.gz.enc`.
- Checksum output: `secure_package/*.tar.gz.enc.sha256`.

Create encrypted package:

```bash
mkdir -p .secrets secure_package
chmod 700 .secrets
openssl rand -base64 48 > .secrets/pedal_passkey.txt
chmod 600 .secrets/pedal_passkey.txt

ts=$(date +%Y%m%d_%H%M%S)
tar -czf "secure_package/pedal_config_${ts}.tar.gz" \
  --exclude='./.git' --exclude='./backups' --exclude='./secure_package' --exclude='./.secrets' .
openssl enc -aes-256-cbc -pbkdf2 -iter 250000 -salt \
  -in "secure_package/pedal_config_${ts}.tar.gz" \
  -out "secure_package/pedal_config_${ts}.tar.gz.enc" \
  -pass file:.secrets/pedal_passkey.txt
shasum -a 256 "secure_package/pedal_config_${ts}.tar.gz.enc" \
  > "secure_package/pedal_config_${ts}.tar.gz.enc.sha256"
rm -f "secure_package/pedal_config_${ts}.tar.gz"
```

Decrypt package:

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 250000 \
  -in secure_package/<archive>.tar.gz.enc \
  -pass file:.secrets/pedal_passkey.txt \
  | tar -xzf - -C /path/to/restore
```

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
- `gate.js` - hostname/passkey unlock flow and app boot loading
- `app.js` - drag/drop logic, recommendation engine, offline save
- `data/config.js` - pedal library, genre presets, amp models, guitar profiles, chain-order rules
- `data/access.js` - hashed hostname access policy used by the unlock gate
