#!/usr/bin/env sh
set -eu

target="${1:-codex}"
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
source_dir="$repo_root/plugins/write-thai-academic-book/skills/write-thai-academic-book"

case "$target" in
  codex|antigravity) base="$HOME/.agents/skills" ;;
  antigravity-cli) base="$HOME/.gemini/antigravity-cli/skills" ;;
  claude-code) base="$HOME/.claude/skills" ;;
  *) echo "Usage: $0 codex|antigravity|antigravity-cli|claude-code" >&2; exit 2 ;;
esac

destination="$base/write-thai-academic-book"
mkdir -p "$base"
rm -rf "$destination"
cp -R "$source_dir" "$destination"
printf 'Installed write-thai-academic-book for %s at %s\n' "$target" "$destination"
