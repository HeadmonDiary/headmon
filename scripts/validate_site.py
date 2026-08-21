#!/usr/bin/env python3
"""Fail closed on unsafe or structurally broken static-site artifacts."""

from __future__ import annotations

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

    viewer_html = SITE / "bv" / "index.html"
    if viewer_html.exists() and "<noscript>" not in viewer_html.read_text(encoding="utf-8"):
        issues.append("the backup viewer must explain that JavaScript is required")

    if issues:
        print("Site validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(f"Validated {len(files)} public files; no sensitive export types or broken references found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
