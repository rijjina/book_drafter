#!/usr/bin/env python3
"""Validate Codex, Claude/Cowork, and Antigravity distribution adapters."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "write-thai-academic-book"
SKILLS = {
    name: PLUGIN / "skills" / name
    for name in (
        "write-thai-academic-book",
        "research-outline-evidence",
        "assess-thai-academic-manuscript",
        "orchestrate-thai-academic-writing",
    )
}
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def read_json(path: Path, errors: list[str]) -> dict:
    if not path.is_file():
        errors.append(f"Missing JSON file: {path.relative_to(ROOT)}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid JSON at {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"JSON root must be an object: {path.relative_to(ROOT)}")
        return {}
    return value


def skill_frontmatter(skill_name: str, errors: list[str]) -> dict[str, str]:
    path = SKILLS[skill_name] / "SKILL.md"
    if not path.is_file():
        errors.append(f"Missing shared skills/{skill_name}/SKILL.md")
        return {}
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if not match:
        errors.append("SKILL.md frontmatter is missing or malformed")
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"\'')
    return fields


def find_market_entry(manifest: dict, errors: list[str], label: str) -> dict:
    plugins = manifest.get("plugins", [])
    if not isinstance(plugins, list):
        errors.append(f"{label} plugins must be an array")
        return {}
    for entry in plugins:
        if isinstance(entry, dict) and entry.get("name") == "write-thai-academic-book":
            return entry
    errors.append(f"{label} has no write-thai-academic-book entry")
    return {}


def main() -> int:
    errors: list[str] = []
    codex = read_json(PLUGIN / ".codex-plugin" / "plugin.json", errors)
    claude = read_json(PLUGIN / ".claude-plugin" / "plugin.json", errors)
    antigravity = read_json(PLUGIN / "plugin.json", errors)
    codex_market = read_json(ROOT / ".agents" / "plugins" / "marketplace.json", errors)
    claude_market = read_json(ROOT / ".claude-plugin" / "marketplace.json", errors)

    version = codex.get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        errors.append(f"Codex plugin version is not strict semver: {version!r}")
    for label, value in (
        ("Claude plugin", claude.get("version")),
        ("Codex marketplace", find_market_entry(codex_market, errors, "Codex marketplace").get("version")),
        ("Claude marketplace", find_market_entry(claude_market, errors, "Claude marketplace").get("version")),
    ):
        if value != version:
            errors.append(f"{label} version {value!r} does not match {version!r}")

    if codex.get("name") != PLUGIN.name or codex.get("skills") != "./skills/":
        errors.append("Codex manifest name/skills path is inconsistent with the plugin folder")
    interface = codex.get("interface", {})
    prompts = interface.get("defaultPrompt", []) if isinstance(interface, dict) else []
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        errors.append("Codex interface.defaultPrompt must contain 1-3 strings")
    elif any(not isinstance(item, str) or len(item) > 128 for item in prompts):
        errors.append("Every Codex defaultPrompt must be a string of at most 128 characters")

    if claude.get("name") != PLUGIN.name:
        errors.append("Claude plugin name does not match the plugin folder")

    expected_antigravity_keys = {"$schema", "name", "description"}
    if set(antigravity) != expected_antigravity_keys:
        errors.append("Antigravity plugin.json must contain only schema, name, and description")
    if antigravity.get("name") != PLUGIN.name:
        errors.append("Antigravity plugin name does not match the plugin folder")

    for skill_name, skill_path in SKILLS.items():
        fields = skill_frontmatter(skill_name, errors)
        if fields.get("name") != skill_name:
            errors.append(f"Shared Skill frontmatter has the wrong name: {skill_name}")
        description = fields.get("description", "")
        if not description or len(description) > 200:
            errors.append(
                f"Shared Skill description must be 1-200 characters: {skill_name}"
            )
        if not (skill_path / "agents" / "openai.yaml").is_file():
            errors.append(f"Shared Skill is missing agents/openai.yaml: {skill_name}")
    if not (SKILLS["write-thai-academic-book"] / "requirements.txt").is_file():
        errors.append("Shared Skill is missing requirements.txt")

    for skill_name in SKILLS:
        package = ROOT / "packages" / f"{skill_name}.zip"
        if not package.is_file():
            errors.append(f"Cowork Skill ZIP is missing: {skill_name}")
            continue
        with zipfile.ZipFile(package) as archive:
            names = [name for name in archive.namelist() if not name.endswith("/")]
        prefix = f"{skill_name}/"
        if not names or any(not name.startswith(prefix) for name in names):
            errors.append(f"Cowork ZIP has the wrong root: {skill_name}")
        if f"{prefix}SKILL.md" not in names:
            errors.append(f"Cowork ZIP is missing SKILL.md: {skill_name}")
        if any(
            "source-pdfs" in name
            or "__pycache__" in name
            or ".reference-cache" in name
            for name in names
        ):
            errors.append(f"Cowork ZIP contains excluded files: {skill_name}")

    powershell = (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
    shell = (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8")
    expected_paths = (
        ".agents\\skills",
        ".gemini\\config\\skills",
        ".gemini\\config\\plugins",
        ".gemini\\antigravity-cli\\plugins",
        ".claude\\skills",
    )
    for path in expected_paths:
        if path not in powershell:
            errors.append(f"PowerShell installer is missing target path {path}")
    for path in (
        ".agents/skills",
        ".gemini/config/skills",
        ".gemini/config/plugins",
        ".gemini/antigravity-cli/plugins",
        ".claude/skills",
    ):
        if path not in shell:
            errors.append(f"Shell installer is missing target path {path}")
    for skill_name in SKILLS:
        if skill_name not in powershell:
            errors.append(f"PowerShell installer omits {skill_name}")
        if skill_name not in shell:
            errors.append(f"Shell installer omits {skill_name}")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "version": version,
        "skills": sorted(SKILLS),
        "platforms": ["codex", "claude-cowork", "claude-code", "antigravity-ide", "antigravity-cli"],
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
