#!/usr/bin/env python3
"""Render the complete education evidence inventory; --check verifies the committed HTML offline.

Requires markdown-it-py. The Markdown note is authoritative; HTML is generated.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import os
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/evidence/edu_last_exam_complete_evidence_inventory_2026-11-10.md"
OUTPUT = ROOT / "reports/research/edu-last-exam-complete-evidence-inventory-2026-11-10.html"

STYLE = """
:root { color-scheme: light; font-family: system-ui, sans-serif; color: #24323c; }
body { margin: 0; background: #f3f5f6; line-height: 1.8; }
main { max-width: 1120px; margin: 32px auto; padding: 36px; background: white; }
h1 { font-size: 1.9rem; line-height: 1.4; }
h2 { margin-top: 2.4em; padding-top: .8em; border-top: 1px solid #d8e0e4; }
a { color: #176b87; overflow-wrap: anywhere; }
p, li, td { overflow-wrap: anywhere; }
nav { padding: 12px 20px; background: #edf5f7; border-radius: 8px; }
nav ul { padding-left: 1.4em; columns: 2; column-gap: 32px; }
nav li { break-inside: avoid; }
.toc-h2 { font-weight: 650; margin-top: .5em; }
.toc-h3 { font-size: .9rem; margin-left: .8em; }
table { border-collapse: collapse; width: 100%; margin: 20px 0; font-size: .92rem; }
th, td { border: 1px solid #d8e0e4; padding: 10px; text-align: left; vertical-align: top; }
th { background: #edf3f5; }
code { font-size: .9em; overflow-wrap: anywhere; }
pre { padding: 16px; background: #edf3f5; overflow-x: auto; line-height: 1.5; }
.provenance { font-size: .85rem; color: #526571; }
@media (max-width: 760px) {
  main { margin: 0; padding: 18px; }
  nav ul { columns: 1; }
  table { display: block; overflow-x: auto; }
  th, td { min-width: 140px; }
}
@media print { body { background: white; } main { margin: 0; padding: 0; } }
"""


def render() -> str:
    source = SOURCE.read_text(encoding="utf-8")
    parser = MarkdownIt("commonmark", {"html": False}).enable("table")
    tokens = parser.parse(source)
    toc = []
    title = "Edu Last Exam 完整证据清单"
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            text = tokens[index + 1].content
            if token.tag == "h1":
                title = text
            if token.tag in {"h2", "h3"}:
                anchor = f"section-{len(toc) + 1}"
                token.attrSet("id", anchor)
                toc.append(f'<li class="toc-{token.tag}"><a href="#{anchor}">{html.escape(text)}</a></li>')
        for child in token.children or []:
            if child.type != "link_open":
                continue
            parts = urlsplit(child.attrGet("href") or "")
            if parts.scheme or parts.netloc or not parts.path:
                continue
            target = (SOURCE.parent / unquote(parts.path)).resolve()
            if not target.exists():
                raise ValueError(f"Missing local research reference: {target}")
            if parts.path.startswith("/"):
                continue
            relative = quote(os.path.relpath(target, OUTPUT.parent), safe="/")
            child.attrSet("href", urlunsplit(("", "", relative, parts.query, parts.fragment)))
    body = parser.renderer.render(tokens, parser.options, {})
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    source_link = os.path.relpath(SOURCE, OUTPUT.parent)
    return (
        '<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{html.escape(title)}</title><style>{STYLE}</style></head><body><main>'
        '<p class="provenance">生成报告 · 证据核验日期 2026-11-10 · '
        f'<a href="{source_link}">Markdown 来源</a><br>Source SHA-256: {digest}</p>'
        f'<nav aria-label="报告目录"><ul>{"".join(toc)}</ul></nav>'
        f'{body}</main></body></html>\n'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without writing")
    args = parser.parse_args()
    result = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != result:
            raise SystemExit("Research HTML is missing or stale; run this script without --check.")
        print("Research HTML matches source; local evidence links exist.")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(result, encoding="utf-8")
        print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
