#!/usr/bin/env python3
"""
Manuscript Audit Tool
Analyzes academic markdown manuscripts for:
- Word counts per section and total body count
- Citation extraction ([@citekey] syntax)
- Verification against .bib bibliography files
- Unresolved placeholders or unverified citations
"""
import argparse
from pathlib import Path
import re
import sys

def parse_frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        return m.group(1), text[m.end():]
    return "", text

def extract_sections(body: str):
    lines = body.splitlines()
    sections = []
    current_sec = "Preamble / Frontmatter"
    current_lines = []

    for line in lines:
        header_match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if header_match:
            if current_lines:
                sections.append((current_sec, "\n".join(current_lines)))
                current_lines = []
            current_sec = header_match.group(2).strip()
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_sec, "\n".join(current_lines)))

    return sections

def count_words(text: str) -> int:
    # Strip markdown comments, image links, and latex math blocks
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)
    text = re.sub(r"\$.*?\$", "", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    words = re.findall(r"\b[A-Za-z0-9_\-]+\b", text)
    return len(words)

def extract_citekeys(text: str) -> set:
    # Find [@key], [@key1; @key2], and @key
    matches = re.findall(r"@([a-zA-Z0-9_\-]+)", text)
    return set(matches)

def parse_bib_keys(bib_path: Path) -> set:
    if not bib_path.exists():
        return set()
    content = bib_path.read_text(encoding="utf-8", errors="ignore")
    # Matches @type{citekey,
    keys = re.findall(r"@[a-zA-Z]+\s*\{\s*([a-zA-Z0-9_\-]+)\s*,", content)
    return set(keys)

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Audit academic manuscript markdown drafts.")
    parser.add_argument("--manuscript", "-m", required=True, help="Path to manuscript markdown file")
    parser.add_argument("--bib", "-b", required=False, help="Path to bibliography .bib file")
    parser.add_argument("--max-words", type=int, default=8000, help="Target maximum word ceiling")
    args = parser.parse_args()

    m_path = Path(args.manuscript)
    if not m_path.exists():
        print(f"Error: Manuscript file not found: {m_path}", file=sys.stderr)
        sys.exit(1)

    raw_text = m_path.read_text(encoding="utf-8", errors="ignore")
    fm, body = parse_frontmatter(raw_text)
    sections = extract_sections(body)

    total_words = count_words(body)
    cited_keys = extract_citekeys(body)

    print("=" * 60)
    print(f"MANUSCRIPT AUDIT REPORT: {m_path.name}")
    print("=" * 60)
    print(f"Total Body Words: {total_words:,} (Ceiling: {args.max_words:,})")
    if total_words > args.max_words:
        print(f"  [!] WARNING: Word count exceeds ceiling by {total_words - args.max_words} words!")
    else:
        print(f"  [OK] Word count is within budget ({args.max_words - total_words} words remaining).")

    print("\n--- Section Word Breakdown ---")
    for sec_name, sec_text in sections:
        sec_w = count_words(sec_text)
        pct = (sec_w / total_words * 100) if total_words > 0 else 0
        print(f"  * {sec_name:<40} : {sec_w:>5} words ({pct:>4.1f}%)")

    # Check for placeholders or unverified flags
    placeholders = re.findall(r"\[(UNVERIFIED|TODO|TBD|FIXME|INSERT|XXX).*?\]", body, re.IGNORECASE)
    print("\n--- Integrity & Placeholders ---")
    if placeholders:
        print(f"  [!] Found {len(placeholders)} unresolved flag(s):")
        for p in placeholders[:10]:
            print(f"      - [{p}]")
    else:
        print("  [OK] Zero unresolved placeholder or [UNVERIFIED] flags detected.")

    print("\n--- Citation Statistics ---")
    print(f"Total Unique Citekeys Found: {len(cited_keys)}")
    for k in sorted(cited_keys)[:8]:
        print(f"  • @{k}")
    if len(cited_keys) > 8:
        print(f"  • ... and {len(cited_keys) - 8} more")

    if args.bib:
        bib_path = Path(args.bib)
        bib_keys = parse_bib_keys(bib_path)
        print(f"\n--- Bibliography Validation ({bib_path.name}) ---")
        print(f"Total Entries in .bib file: {len(bib_keys)}")

        missing_in_bib = cited_keys - bib_keys
        if missing_in_bib:
            print(f"  [!] MISSING IN .BIB ({len(missing_in_bib)} keys cited in text but not found in bibliography):")
            for mk in sorted(missing_in_bib):
                print(f"      - @{mk}")
        else:
            print("  [OK] All cited keys are present in the bibliography database.")

        unused_in_bib = bib_keys - cited_keys
        if unused_in_bib:
            print(f"  [*] Uncited entries in .bib ({len(unused_in_bib)} entries defined but not cited in text).")

    print("=" * 60)

if __name__ == "__main__":
    main()
