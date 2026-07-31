#!/usr/bin/env python3
"""Export the canonical local skill and build a deterministic distribution ZIP.

The directory containing this script is always the source of truth. Public Git
working copies and ZIP packages are derived outputs and never flow back into it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = SKILL_DIR.parent
DEFAULT_EXPORT = (
    REPOSITORY_ROOT
    / "github-export"
    / "write-thai-academic-book"
    / "plugins"
    / "write-thai-academic-book"
    / "skills"
    / "write-thai-academic-book"
)
DEFAULT_ZIP = (
    REPOSITORY_ROOT
    / "github-export"
    / "write-thai-academic-book"
    / "packages"
    / "write-thai-academic-book.zip"
)
ZIP_PREFIX = "write-thai-academic-book"
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
    if relative.name.startswith("~$"):
        return False
    return True


def included_files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in sorted(root.rglob("*"))
        if path.is_file() and is_included(path.relative_to(root))
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fingerprints(root: Path) -> dict[str, str]:
    return {name: sha256(path) for name, path in included_files(root).items()}


def validate_export_target(source: Path, export: Path) -> None:
    source = source.resolve()
    export = export.resolve()
    expected_parent = (
        REPOSITORY_ROOT
        / "github-export"
        / "write-thai-academic-book"
        / "plugins"
        / "write-thai-academic-book"
        / "skills"
    ).resolve()
    if export.parent != expected_parent or export.name != "write-thai-academic-book":
        raise RuntimeError(f"Refusing unsafe export target: {export}")
    if export == source or source in export.parents:
        raise RuntimeError(f"Export target overlaps canonical source: {export}")


def remove_tree(path: Path) -> None:
    """Remove a validated export tree, including OneDrive read-only entries."""

    def make_writable_and_retry(function, target, _error):
        Path(target).chmod(stat.S_IWRITE)
        function(target)

    shutil.rmtree(path, onexc=make_writable_and_retry)


def sync_export(source: Path, export: Path) -> None:
    validate_export_target(source, export)
    export.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="write-thai-academic-book-package-", dir=str(export.parent)
    ) as temp_name:
        staged = Path(temp_name) / export.name
        for relative, source_path in included_files(source).items():
            target = staged / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target)
        if export.exists():
            remove_tree(export)
        staged.replace(export)


def build_zip(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix="write-thai-academic-book-", suffix=".zip", dir=output.parent, delete=False
    ) as stream:
        temp_zip = Path(stream.name)
    try:
        with zipfile.ZipFile(
            temp_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            for relative, path in included_files(source).items():
                info = zipfile.ZipInfo(
                    f"{ZIP_PREFIX}/{relative}", date_time=FIXED_ZIP_TIME
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
        temp_zip.replace(output)
    finally:
        if temp_zip.exists():
            temp_zip.unlink()


def zip_fingerprints(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    prefix = f"{ZIP_PREFIX}/"
    with zipfile.ZipFile(path) as archive:
        result: dict[str, str] = {}
        for name in archive.namelist():
            if name.endswith("/") or not name.startswith(prefix):
                continue
            relative = name[len(prefix) :]
            result[relative] = hashlib.sha256(archive.read(name)).hexdigest()
        return result


def parity_report(source: Path, export: Path, package: Path) -> dict[str, object]:
    canonical = fingerprints(source)
    exported = fingerprints(export) if export.is_dir() else {}
    zipped = zip_fingerprints(package)
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
    parser.add_argument("--export", type=Path, default=DEFAULT_EXPORT)
    parser.add_argument("--zip", type=Path, default=DEFAULT_ZIP)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = SKILL_DIR.resolve()
    export = args.export.resolve()
    package = args.zip.resolve()
    if not args.check:
        sync_export(source, export)
        build_zip(source, package)
    report = parity_report(source, export, package)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "MATCH" else 2


if __name__ == "__main__":
    raise SystemExit(main())
