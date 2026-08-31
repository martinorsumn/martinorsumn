#!/usr/bin/env python3
"""Offline preview server for the profile README.

Renders GitHub-flavored Markdown entirely locally (no network calls, no GitHub
API, no secrets) and serves it with a GitHub-like stylesheet plus live reload.
This is the application launched by the ``readme-preview`` terminal in the
Cloud Agent environment so you can see exactly how edits to ``README.md`` look.
"""
from __future__ import annotations

import html
import os
from pathlib import Path

import markdown
from flask import Flask, Response, abort, request
from pygments.formatters import HtmlFormatter

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DOC = os.environ.get("PREVIEW_FILE", "README.md")
HOST = os.environ.get("PREVIEW_HOST", "0.0.0.0")
PORT = int(os.environ.get("PREVIEW_PORT", "6419"))

MD_EXTENSIONS = [
    "extra",  # tables, fenced code, footnotes, attr_list, def lists
    "codehilite",  # Pygments-based syntax highlighting
    "sane_lists",
    "toc",
    "admonition",
]
MD_EXTENSION_CONFIGS = {
    "codehilite": {"guess_lang": False},
}

app = Flask(__name__)

_PYGMENTS_CSS = HtmlFormatter(style="default").get_style_defs(".codehilite")

PAGE_CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #f6f8fa;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  color: #1f2328;
}
.topbar {
  background: #24292f;
  color: #fff;
  padding: 12px 24px;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.topbar .dot { color: #2da44e; }
.wrapper { max-width: 900px; margin: 24px auto; padding: 0 16px; }
.markdown-body {
  background: #fff;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  padding: 32px 40px;
  font-size: 16px;
  line-height: 1.5;
  word-wrap: break-word;
}
.markdown-body h1, .markdown-body h2 {
  border-bottom: 1px solid #d8dee4;
  padding-bottom: .3em;
}
.markdown-body h1 { font-size: 2em; margin: .67em 0; }
.markdown-body h2 { font-size: 1.5em; margin-top: 24px; }
.markdown-body h3 { font-size: 1.25em; }
.markdown-body a { color: #0969da; text-decoration: none; }
.markdown-body a:hover { text-decoration: underline; }
.markdown-body ul, .markdown-body ol { padding-left: 2em; }
.markdown-body li { margin-top: .25em; }
.markdown-body code {
  background: rgba(175,184,193,.2);
  padding: .2em .4em;
  border-radius: 6px;
  font-size: 85%;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
}
.markdown-body pre {
  background: #f6f8fa;
  padding: 16px;
  border-radius: 6px;
  overflow: auto;
}
.markdown-body pre code { background: transparent; padding: 0; }
.markdown-body table { border-collapse: collapse; }
.markdown-body table th, .markdown-body table td {
  border: 1px solid #d0d7de;
  padding: 6px 13px;
}
.markdown-body blockquote {
  border-left: .25em solid #d0d7de;
  color: #656d76;
  padding: 0 1em;
  margin: 0;
}
.markdown-body img { max-width: 100%; }
"""

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} · Preview</title>
  <style>{page_css}</style>
  <style>{pygments_css}</style>
</head>
<body>
  <div class="topbar">
    <span><span class="dot">&#9679;</span> Offline README preview &mdash; {doc}</span>
    <span>auto-reloads on save</span>
  </div>
  <div class="wrapper">
    <article class="markdown-body">{content}</article>
  </div>
  <script>
    let last = "{mtime}";
    async function poll() {{
      try {{
        const r = await fetch("/__status?doc={doc}");
        const j = await r.json();
        if (String(j.mtime) !== last) {{ location.reload(); }}
      }} catch (e) {{ /* server restarting */ }}
    }}
    setInterval(poll, 1000);
  </script>
</body>
</html>"""


def _resolve_doc(doc: str) -> Path:
    """Resolve a requested markdown file safely within the repo root."""
    candidate = (REPO_ROOT / doc).resolve()
    if not str(candidate).startswith(str(REPO_ROOT)):
        abort(403)
    if candidate.suffix.lower() not in {".md", ".markdown"} or not candidate.is_file():
        abort(404)
    return candidate


def _render(path: Path) -> str:
    md = markdown.Markdown(
        extensions=MD_EXTENSIONS, extension_configs=MD_EXTENSION_CONFIGS
    )
    return md.convert(path.read_text(encoding="utf-8"))


@app.get("/")
def index() -> Response:
    doc = request.args.get("doc", DEFAULT_DOC)
    path = _resolve_doc(doc)
    page = PAGE_TEMPLATE.format(
        title=html.escape(path.stem),
        doc=html.escape(doc),
        page_css=PAGE_CSS,
        pygments_css=_PYGMENTS_CSS,
        content=_render(path),
        mtime=path.stat().st_mtime,
    )
    return Response(page, mimetype="text/html")


@app.get("/__status")
def status() -> Response:
    doc = request.args.get("doc", DEFAULT_DOC)
    path = _resolve_doc(doc)
    return {"doc": doc, "mtime": path.stat().st_mtime}


@app.get("/healthz")
def healthz() -> Response:
    return {"status": "ok", "doc": DEFAULT_DOC}


if __name__ == "__main__":
    print(f"Serving offline README preview at http://{HOST}:{PORT} ({DEFAULT_DOC})")
    app.run(host=HOST, port=PORT, threaded=True)
