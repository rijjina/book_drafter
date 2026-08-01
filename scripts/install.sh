#!/usr/bin/env sh
set -eu

target="${1:-codex}"
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
skills_dir="$repo_root/plugins/write-thai-academic-book/skills"
skill_names="write-thai-academic-book research-outline-evidence assess-thai-academic-manuscript orchestrate-thai-academic-writing"

case "$target" in
  codex) base="$HOME/.agents/skills"; kind="skills" ;;
  antigravity) base="$HOME/.gemini/config/skills"; kind="skills" ;;
  antigravity-plugin) base="$HOME/.gemini/config/plugins"; source_path="$repo_root/plugins/write-thai-academic-book"; kind="plugin" ;;
  antigravity-cli) base="$HOME/.gemini/antigravity-cli/plugins"; source_path="$repo_root/plugins/write-thai-academic-book"; kind="plugin" ;;
  claude-code) base="$HOME/.claude/skills"; kind="skills" ;;
  *) echo "Usage: $0 codex|antigravity|antigravity-plugin|antigravity-cli|claude-code" >&2; exit 2 ;;
esac

mkdir -p "$base"
if [ "$kind" = "plugin" ]; then
  destination="$base/write-thai-academic-book"
  rm -rf "$destination"
  cp -R "$source_path" "$destination"
  printf 'Installed Thai academic writing suite plugin for %s at %s\n' "$target" "$destination"
  exit 0
fi

for skill_name in $skill_names; do
  destination="$base/$skill_name"
  rm -rf "$destination"
  cp -R "$skills_dir/$skill_name" "$destination"
  printf 'Installed %s skill for %s at %s\n' "$skill_name" "$target" "$destination"
done
