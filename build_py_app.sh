#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

STAMP="$(date '+%Y-%m-%d_%H%M%S')"
BACKUP_DIR="$ROOT_DIR/backups/executable_backup_${STAMP}"
mkdir -p "$BACKUP_DIR"

backup_artifact() {
  local src="$1"
  if [[ -e "$src" ]]; then
    local name
    name="$(basename "$src")"
    if [[ -e "$BACKUP_DIR/$name" ]]; then
      name="${name}_$(date '+%H%M%S')"
    fi
    mv "$src" "$BACKUP_DIR/$name"
  fi
}

backup_artifact "$ROOT_DIR/PedalArchitect.app"
backup_artifact "$ROOT_DIR/PedalArchitect"
backup_artifact "$ROOT_DIR/dist/PedalArchitect.app"
backup_artifact "$ROOT_DIR/dist/PedalArchitect"

pyinstaller --noconfirm --clean --distpath "$ROOT_DIR" --workpath "$ROOT_DIR/build" PedalArchitect.spec

if [[ -d "$ROOT_DIR/dist" ]] && [[ -z "$(ls -A "$ROOT_DIR/dist" 2>/dev/null)" ]]; then
  rmdir "$ROOT_DIR/dist"
fi

echo "Build complete. Executable written to: $ROOT_DIR/PedalArchitect.app"
echo "Previous executable backup: $BACKUP_DIR"
