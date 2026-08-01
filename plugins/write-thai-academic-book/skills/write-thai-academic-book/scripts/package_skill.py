#!/usr/bin/env python3
"""Export the canonical Thai academic-writing skill suite deterministically."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DISTRIBUTION = (
    SKILL_DIR.parent.name == "skills"
    and (SKILL_DIR.parent.parent / ".codex-plugin" / "plugin.json").is_file()
)
WORKSPACE_ROOT = SKILL_DIR.parent if PUBLIC_DISTRIBUTION else SKILL_DIR.parent
DIST_ROOT = (
    SKILL_DIR.parents[3]
    if PUBLIC_DISTRIBUTION
    else WORKSPACE_ROOT / "github-export" / "write-thai-academic-book"
)
PLUGIN_SKILLS = (
    SKILL_DIR.parent
    if PUBLIC_DISTRIBUTION
    else DIST_ROOT / "plugins" / "write-thai-academic-book" / "skills"
)
PACKAGE_ROOT = DIST_ROOT / "packages"
SKILL_SOURCES = (
    {
        name: PLUGIN_SKILLS / name
        for name in (
            "write-thai-academic-book",
            "research-outline-evidence",
            "assess-thai-academic-manuscript",
            "orchestrate-thai-academic-writing",
        )
    }
    if PUBLIC_DISTRIBUTION
    else {
        "write-thai-academic-book": SKILL_DIR,
        "research-outline-evidence": WORKSPACE_ROOT / "research-outline-evidence",
        "assess-thai-academic-manuscript": WORKSPACE_ROOT / "assess-thai-academic-manuscript",
        "orchestrate-thai-academic-writing": WORKSPACE_ROOT / "orchestrate-thai-academic-writing",
    }
)
FIXED_ZIP_TIME = (2000, 1, 1, 0, 0, 0)
EXCLUDED_DIRECTORY_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".reference-cache",
    ".docx-build",
    "rendered",
}
EXCLUDED_FILE_SUFFIXES = {".pyc", ".pyo"}


def is_included(relative: Path) -> bool:
    if "source-pdfs" in relative.parts:
        return False
    if any(part in EXCLUDED_DIRECTORY_NAMES for part in relative.parts):
        return False
    if relative.suffix.lower() in EXCLUDED_FILE_SUFFIXES:
        return False
    return not relative.name.startswith("~$")


def included_files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in sorted(root.rglob("*"))
        if path.is_file() and is_included(path.relative_to(root))
    }


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fingerprints(root: Path) -> dict[str, str]:
    return {
        name: sha256_bytes(path.read_bytes())
        for name, path in included_files(root).items()
    }


def validate_export_target(export: Path, skill_name: str) -> None:
    export = export.resolve()
    if export.parent != PLUGIN_SKILLS.resolve() or export.name != skill_name:
        raise RuntimeError(f"Refusing unsafe export target: {export}")


def sync_export(source: Path, export: Path, skill_name: str) -> None:
    """Synchronize in place so cloud-backed folders do not see a tree deletion."""

    validate_export_target(export, skill_name)
    export.mkdir(parents=True, exist_ok=True)
    canonical = included_files(source)
    exported = {
        path.relative_to(export).as_posix(): path
        for path in export.rglob("*")
        if path.is_file()
    }
    for relative, target in exported.items():
        if relative not in canonical:
            target.chmod(0o666)
            target.unlink()
    for relative, source_path in canonical.items():
        target = export / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.chmod(0o666)
        shutil.copy2(source_path, target)
    for directory in sorted(
        (path for path in export.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        if not any(directory.iterdir()):
            directory.rmdir()


def build_zip(source: Path, output: Path, skill_name: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f"{skill_name}-", suffix=".zip", dir=output.parent, delete=False
    ) as stream:
        temp_zip = Path(stream.name)
    try:
        with zipfile.ZipFile(
            temp_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            for relative, path in included_files(source).items():
                info = zipfile.ZipInfo(
                    f"{skill_name}/{relative}", date_time=FIXED_ZIP_TIME
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
        temp_zip.replace(output)
    finally:
        if temp_zip.exists():
            temp_zip.unlink()


def zip_fingerprints(path: Path, skill_name: str) -> dict[str, str]:
    if not path.is_file():
        return {}
    prefix = f"{skill_name}/"
    with zipfile.ZipFile(path) as archive:
        return {
            name[len(prefix) :]: sha256_bytes(archive.read(name))
            for name in archive.namelist()
            if not name.endswith("/") and name.startswith(prefix)
        }


def skill_report(skill_name: str, source: Path) -> dict[str, object]:
    export = PLUGIN_SKILLS / skill_name
    package = PACKAGE_ROOT / f"{skill_name}.zip"
    canonical = fingerprints(source)
    exported = fingerprints(export) if export.is_dir() else {}
    zipped = zip_fingerprints(package, skill_name)
    return {
        "status": "MATCH" if canonical == exported == zipped else "MISMATCH",
        "canonical_source": str(source),
        "export_target": str(export),
        "package_target": str(package),
        "canonical_files": len(canonical),
        "export_files": len(exported),
        "zip_files": len(zipped),
        "export_matches": canonical == exported,
        "zip_matches": canonical == zipped,
        "excluded_source_pdfs": not any("source-pdfs" in name for name in zipped),
        "excluded_caches": not any(
            "__pycache__" in name
            or ".pytest_cache" in name
            or ".reference-cache" in name
            or name.endswith(".pyc")
            for name in zipped
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check parity without writing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if PUBLIC_DISTRIBUTION and not args.check:
        raise RuntimeError("The public distribution is check-only; package from the canonical workspace.")
    missing = [name for name, path in SKILL_SOURCES.items() if not path.is_dir()]
    if missing:
        raise RuntimeError(f"Missing canonical skill directories: {', '.join(missing)}")
    if not args.check:
        for name, source in SKILL_SOURCES.items():
            sync_export(source.resolve(), PLUGIN_SKILLS / name, name)
            build_zip(source.resolve(), PACKAGE_ROOT / f"{name}.zip", name)
    skills = {name: skill_report(name, source.resolve()) for name, source in SKILL_SOURCES.items()}
    writer = skills["write-thai-academic-book"]
    report = {
        "status": "MATCH" if all(item["status"] == "MATCH" for item in skills.values()) else "MISMATCH",
        "canonical_files": writer["canonical_files"],
        "export_matches": writer["export_matches"],
        "zip_matches": writer["zip_matches"],
        "excluded_source_pdfs": all(item["excluded_source_pdfs"] for item in skills.values()),
        "excluded_caches": all(item["excluded_caches"] for item in skills.values()),
        "skills": skills,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "MATCH" else 2


if __name__ == "__main__":
    raise SystemExit(main())
