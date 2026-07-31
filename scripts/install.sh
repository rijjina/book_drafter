#!/usr/bin/env sh
set -eu

target="${1:-codex}"
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
source_dir="$repo_root/plugins/write-thai-academic-book/skills/write-thai-academic-book"

case "$target" in
  codex) base="$HOME/.agents/skills"; source_path="$source_dir"; kind="skill" ;;
  antigravity) base="$HOME/.gemini/config/skills"; source_path="$source_dir"; kind="skill" ;;
  antigravity-plugin) base="$HOME/.gemini/config/plugins"; source_path="$repo_root/plugins/write-thai-academic-book"; kind="plugin" ;;
  antigravity-cli) base="$HOME/.gemini/antigravity-cli/plugins"; source_path="$repo_root/plugins/write-thai-academic-book"; kind="plugin" ;;
  claude-code) base="$HOME/.claude/skills"; source_path="$source_dir"; kind="skill" ;;
  *) echo "Usage: $0 codex|antigravity|antigravity-plugin|antigravity-cli|claude-code" >&2; exit 2 ;;
esac

destination="$base/write-thai-academic-book"
mkdir -p "$base"
rm -rf "$destination"
cp -R "$source_path" "$destination"
printf 'Installed write-thai-academic-book %s for %s at %s\n' "$kind" "$target" "$destination"
