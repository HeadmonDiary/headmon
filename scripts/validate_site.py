#!/usr/bin/env python3
"""Fail closed on unsafe or structurally broken static-site artifacts."""

from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
FORBIDDEN_SUFFIXES = {
    ".csv",
    ".db",
    ".json",
    ".pdf",
    ".sqlite",
    ".sqlite3",
    ".zip",
}


class References(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)


def local_target(document: Path, reference: str) -> Path | None:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or reference.startswith(("#", "mailto:", "tel:")):
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    target = SITE / path.lstrip("/") if path.startswith("/") else document.parent / path
    if path.endswith("/"):
        target /= "index.html"
    return target.resolve()


def main() -> int:
    issues: list[str] = []
    files = [path for path in SITE.rglob("*") if path.is_file()]

    for path in files:
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            issues.append(f"sensitive export type must not be published: {relative}")
        if path.name.endswith(".map"):
            issues.append(f"source map must not be published: {relative}")

    for document in sorted(SITE.rglob("*.html")):
        text = document.read_text(encoding="utf-8")
        relative = document.relative_to(ROOT)
        if 'http-equiv="Content-Security-Policy"' not in text:
            issues.append(f"missing Content Security Policy: {relative}")
        if '<meta name="referrer" content="no-referrer"' not in text:
            issues.append(f"missing no-referrer policy: {relative}")
        if document != SITE / "bv" / "index.html":
            if 'class="skip-link"' not in text or 'id="main-content"' not in text:
                issues.append(f"missing keyboard skip link or main target: {relative}")

        parser = References()
        parser.feed(text)
        for reference in parser.references:
            target = local_target(document, reference)
            if target is None:
                continue
            try:
                target.relative_to(SITE.resolve())
            except ValueError:
                issues.append(f"reference escapes site root in {relative}: {reference}")
                continue
            if target.is_dir():
                target /= "index.html"
            if not target.exists():
                issues.append(f"broken local reference in {relative}: {reference}")

    viewer_scripts = list((SITE / "bv" / "assets").glob("*.js"))
    viewer_styles = list((SITE / "bv" / "assets").glob("*.css"))
    if len(viewer_scripts) != 1:
        issues.append("the backup viewer must have exactly one JavaScript bundle")
    else:
        viewer = viewer_scripts[0].read_text(encoding="utf-8")
        if "indexedDB.open" in viewer:
            issues.append("the backup viewer must not open persistent browser storage")
        if "deleteDatabase" not in viewer:
            issues.append("the backup viewer must remove its legacy draft database")
        if "window.top" not in viewer or "does not run the backup viewer inside another website" not in viewer:
            issues.append("the backup viewer must refuse framed operation")
    if len(viewer_styles) != 1:
        issues.append("the backup viewer must have exactly one CSS bundle")

    viewer_html = SITE / "bv" / "index.html"
    if viewer_html.exists() and "<noscript>" not in viewer_html.read_text(encoding="utf-8"):
        issues.append("the backup viewer must explain that JavaScript is required")

    viewer_source = SITE / "bv" / "SOURCE.txt"
    viewer_license = SITE / "bv" / "LICENSE.txt"
    viewer_notices = SITE / "bv" / "THIRD_PARTY_NOTICES.txt"
    for required_file in (viewer_source, viewer_license, viewer_notices):
        if not required_file.exists():
            issues.append(f"missing backup viewer distribution file: {required_file.relative_to(ROOT)}")

    if viewer_source.exists():
        source_text = viewer_source.read_text(encoding="utf-8")
        if "https://github.com/HeadmonDiary/headmon-backup-viewer" not in source_text:
            issues.append("the backup viewer must link to its corresponding source")
        if not re.search(r"Source revision:\s+[0-9a-f]{40}\b", source_text):
            issues.append("the backup viewer must record an exact source revision")
        built_files = [viewer_html, SITE / "bv" / "headmon-icon.png", *viewer_scripts, *viewer_styles]
        for built_file in built_files:
            if not built_file.exists():
                continue
            digest = hashlib.sha256(built_file.read_bytes()).hexdigest()
            relative = built_file.relative_to(SITE / "bv").as_posix()
            if f"{digest}  {relative}" not in source_text:
                issues.append(f"stale or missing viewer build hash: {relative}")

    if issues:
        print("Site validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(f"Validated {len(files)} public files; no sensitive export types or broken references found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
