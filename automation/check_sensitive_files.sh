#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

SENSITIVE_REGEX='(^|/)AGENTS\.md$|(^|/).*config.*\.(json|ya?ml|toml|ini|cfg|js)$'

tracked_hits="$(
  while IFS= read -r path; do
    [[ -e "$path" ]] || continue
    printf '%s\n' "$path"
  done < <(git ls-files) | rg -n "$SENSITIVE_REGEX" || true
)"
staged_hits="$(
  git diff --cached --name-status | awk '$1 != "D" {print $2}' | rg -n "$SENSITIVE_REGEX" || true
)"

if [[ -n "$tracked_hits" ]]; then
  echo "Blocked: tracked sensitive files detected:"
  echo "$tracked_hits"
  exit 1
fi

if [[ -n "$staged_hits" ]]; then
  echo "Blocked: staged sensitive files detected:"
  echo "$staged_hits"
  exit 1
fi

echo "Sensitive-file scan passed."
