#!/usr/bin/env python3
"""Validate the portable Hermes + Obsidian academic-writing integration."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INTEGRATION = ROOT / "integrations" / "hermes-obsidian"

EXPECTED_SKILLS = {
    "abstract-title",
    "academic-editing",
    "academic-writing-vault",
    "citations-bibtex",
    "data-analysis-viz",
    "discussion-implications",
    "intro-framing",
    "journal-submission",
    "literature-intake",
    "manuscript-orchestrator",
    "methods-protocol",
    "peer-review-rebuttal",
    "research-5chapters",
    "results-reporting",
    "study-spec",
    "systematic-review",
    "thai-academic-teaching-material",
}

REQUIRED = (
    INTEGRATION / "README.md",
    INTEGRATION / "hermes-config.example.yaml",
    INTEGRATION / "skills" / "academic-writing-vault" / "SKILL.md",
    INTEGRATION / "skills" / "thai-academic-teaching-material" / "SKILL.md",
    INTEGRATION
    / "skills"
    / "thai-academic-teaching-material"
    / "references"
    / "generalized-teaching-writing-style.md",
    INTEGRATION
    / "skills"
    / "thai-academic-teaching-material"
    / "assets"
    / "generic-teaching-chapter-template.md",
    INTEGRATION
    / "skills"
    / "thai-academic-teaching-material"
    / "agents"
    / "openai.yaml",
    INTEGRATION / "skills" / "manuscript-orchestrator" / "SKILL.md",
    INTEGRATION / "agents" / "AGENTS.md",
    INTEGRATION / "agents" / "quanta" / "SOUL.md",
    INTEGRATION / "agents" / "nova" / "SOUL.md",
    INTEGRATION / "agents" / "aegis" / "SOUL.md",
    INTEGRATION / "references" / "academic-integrity-gates.md",
    INTEGRATION / "templates" / "MANUSCRIPT_TEMPLATE.md",
    INTEGRATION / "vault-template" / "AGENTS.md",
    INTEGRATION / "vault-template" / "00-HOME.md",
    INTEGRATION / "vault-template" / "AI-SHARED-CONTEXT.md",
    INTEGRATION / "vault-template" / "Templates" / "PROJECT.md",
    INTEGRATION / "vault-template" / "Templates" / "HANDOFF.md",
    ROOT / "scripts" / "setup-hermes-obsidian.ps1",
)

FORBIDDEN_PATHS = (
    re.compile(r"[A-Za-z]:[\\/](?:Users|OneDrive|AI)[\\/]", re.IGNORECASE),
    re.compile(r"/home/[^/<\s]+/"),
)

SECRET_ASSIGNMENT = re.compile(
    r"(?im)^\s*(?:api[_-]?key|token|password|secret|cookie)\s*[:=]\s*(?!<|\$|\{|\[|$).+"
)


def skill_name(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return None
    name = re.search(r"(?m)^name:\s*([^\n]+)$", match.group(1))
    return name.group(1).strip().strip("'\"") if name else None


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.is_file():
            errors.append(f"missing: {path.relative_to(ROOT)}")

    skills_dir = INTEGRATION / "skills"
    if skills_dir.is_dir():
        names: set[str] = set()
        for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
            name = skill_name(skill_file)
            if not name:
                errors.append(f"invalid frontmatter: {skill_file.relative_to(ROOT)}")
                continue
            if name != skill_file.parent.name:
                errors.append(
                    f"skill name/folder mismatch: {skill_file.relative_to(ROOT)} ({name})"
                )
            if name in names:
                errors.append(f"duplicate skill name: {name}")
            names.add(name)
        missing = sorted(EXPECTED_SKILLS - names)
        unexpected = sorted(names - EXPECTED_SKILLS)
        if missing:
            errors.append(f"missing skills: {', '.join(missing)}")
        if unexpected:
            errors.append(f"unexpected skills: {', '.join(unexpected)}")

    for path in sorted(INTEGRATION.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".py",
            ".ps1",
            ".yaml",
            ".yml",
            ".json",
        }:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATHS:
            if pattern.search(text):
                errors.append(f"machine-specific absolute path: {path.relative_to(ROOT)}")
                break
        if SECRET_ASSIGNMENT.search(text):
            errors.append(f"possible committed secret: {path.relative_to(ROOT)}")

    status = "PASS" if not errors else "FAIL"
    print(f"Hermes + Obsidian portability validation: {status}")
    for error in errors:
        print(f"- {error}")
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
