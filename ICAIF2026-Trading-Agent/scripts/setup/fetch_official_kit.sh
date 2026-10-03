#!/usr/bin/env bash
# Fetch the official ICAIF 2026 starter kit at a pinned commit into third_party/ (git-ignored).
# The kit has no explicit licence, so it is referenced, not vendored into this repository.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$ROOT/third_party/icaif_starter_kit"
REPO="https://github.com/DeepIntoStreams/2026ICAIF_Trading_Agent_Competition.git"
COMMIT="${ICAIF_KIT_COMMIT:-ad237b074d31dca39c5c975b3e5cb61cf85a8feb}"
if [ ! -d "$DEST/.git" ]; then
  git clone --quiet "$REPO" "$DEST"
fi
git -C "$DEST" fetch --quiet origin
git -C "$DEST" checkout --quiet "$COMMIT"
echo "official kit at $(git -C "$DEST" rev-parse HEAD) -> $DEST/starter-kit"
if [ "$COMMIT" != "$(git -C "$DEST" rev-parse origin/main)" ]; then
  echo "NOTE: origin/main is now $(git -C "$DEST" rev-parse origin/main); review upstream changes before re-pinning." >&2
fi
