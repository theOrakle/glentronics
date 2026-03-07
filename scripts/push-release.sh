#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SHARED="$REPO_DIR/../release/push-release.sh"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOH'
Usage:
  ./scripts/push-release.sh [tag]
EOH
  exit 0
fi

if [[ ! -x "$SHARED" ]]; then
  echo "Missing shared push script: $SHARED" >&2
  exit 1
fi

exec "$SHARED" "$REPO_DIR" "$@"
