#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

ARCH="${1:-arm64}"
case "$ARCH" in
  arm64|x86_64|universal2) ;;
  *)
    echo "Unsupported macOS arch: $ARCH"
    echo "Use: arm64 | x86_64 | universal2"
    exit 1
    ;;
esac

STAMP="$(date '+%Y-%m-%d_%H%M%S')"
BACKUP_DIR="$ROOT_DIR/backups/executable_backup_${STAMP}"
mkdir -p "$BACKUP_DIR"

backup_artifact() {
  local src="$1"
  if [[ -e "$src" ]]; then
    local name
    name="$(basename "$src")"
    mv "$src" "$BACKUP_DIR/$name"
  fi
}

backup_artifact "$ROOT_DIR/PedalArchitect.app"
backup_artifact "$ROOT_DIR/PedalArchitect"

pyinstaller --noconfirm --clean \
  --target-arch "$ARCH" \
  --distpath "$ROOT_DIR" \
  --workpath "$ROOT_DIR/build/${ARCH}" \
  PedalArchitect.spec

echo "macOS build complete for $ARCH"
echo "Backup directory: $BACKUP_DIR"
