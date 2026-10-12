"""Build the private reading copy of the methods page as one HTML file.

Renders the Quarto site in a temporary folder (as scripts/check_site.py
does), takes the body of methods.html and wraps it with the design tokens
from theme/tokens.json, so the copy can be read without the site. The
numbers are whatever the render read from results/; nothing is typed here.

Run inside the whiplash env, from the repo root:
    python scripts/build_methods_copy.py --out <path to .html>
"""
from __future__ import annotations

import argparse
import base64
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import check_site  # noqa: E402
from src import theme  # noqa: E402

MAIN = re.compile(r"<main\b[^>]*>(.*)</main>", re.DOTALL)
IMG_SRC = re.compile(r'(?<=<img )src="([^"]+)"')
MEDIA_TYPES = {".svg": "image/svg+xml", ".png": "image/png"}
# Figures are drawn on the light surface, so their panel keeps that ground.
PAGE_CSS = """
body { background: var(--page); color: var(--ink); font: 16px/1.62 var(--font-sans); }
.page { max-width: 980px; margin: 0 auto; padding-inline: 20px; padding-block: 32px 72px; }
.stamp { font: 0.76rem var(--font-mono); color: var(--ink-muted); margin-bottom: 18px; }
h1, h2, h3 { font-family: var(--font-display); text-wrap: balance; line-height: 1.18; margin: 0; }
h1 { font-size: 2.5rem; font-weight: 800; letter-spacing: -0.01em; margin-bottom: 20px; }
h2 { font-size: 1.625rem; font-weight: 700; margin-top: 52px; padding-top: 18px;
  border-top: var(--stroke-mark) solid var(--evergreen); }
h3 { font-size: 1.125rem; font-weight: 700; margin-top: 30px; }
p, ul, blockquote { max-width: 68ch; }
p { margin: 12px 0 0; }
ul { margin: 12px 0 0; padding-left: 20px; display: grid; gap: 8px; }
strong { font-weight: 600; }
code { font: 0.86em var(--font-mono); background: var(--surface-sunk); padding: 1px 4px;
  border-radius: var(--radius-sm); }
a { color: var(--evergreen); text-decoration-color: var(--rule-strong); overflow-wrap: anywhere; }
blockquote { margin: 14px 0 0; padding: 2px 0 2px 14px; border-left: 3px solid var(--rule);
  color: var(--ink-muted); }
.callout { background: var(--surface-sunk); border-top: var(--stroke-mark) solid var(--evergreen);
  border-radius: 0 0 var(--radius-md) var(--radius-md); padding: 12px 16px; margin: 0 0 8px;
  max-width: 68ch; }
.callout .callout-title-container { font: 600 0.72rem var(--font-sans); letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--ink-muted); }
.callout .callout-icon-container, .screen-reader-only { display: none; }
.callout p { margin-top: 6px; }
table { border-collapse: collapse; font-size: 0.86rem; width: 100%; background: var(--surface); }
.tablewrap { overflow-x: auto; margin-top: 16px; border: 1px solid var(--rule);
  border-radius: var(--radius-md); }
th, td { padding: 6px 11px; border-bottom: 1px solid var(--rule); text-align: left;
  vertical-align: top; }
th { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink-muted);
  font-weight: 600; border-bottom-color: var(--rule-strong); white-space: nowrap; }
td[style*="right"], th[style*="right"] { font-family: var(--font-mono);
  font-variant-numeric: tabular-nums; white-space: nowrap; }
tr:last-child td { border-bottom: 0; }
td strong { color: var(--evergreen); }
.cell-output-display { overflow-x: auto; margin-top: 16px; background: __FIGURE_GROUND__;
  border: 1px solid var(--rule); border-radius: var(--radius-md); padding: 10px; }
.cell-output-display svg, .cell-output-display img { max-width: 100%; height: auto;
  display: block; margin: 0 auto; }
figure { margin: 0; }
.d-none { display: none; }
@media (min-width: 576px) { .d-sm-block { display: block; } .d-sm-none { display: none; } }
.quarto-title-meta { display: none; }
"""


def _inline_images(html: str, folder: Path) -> str:
    """Replace each local image path with the file itself as a data URI, so
    the copy is one file. Remote and already-inlined sources are left alone."""
    def swap(match: re.Match) -> str:
        src = match.group(1)
        target = folder / src
        if "://" in src or src.startswith("data:") or not target.is_file():
            return match.group(0)
        kind = MEDIA_TYPES.get(target.suffix.lower())
        if kind is None:
            raise ValueError(f"No media type for {target.name}; add it to MEDIA_TYPES.")
        data = base64.b64encode(target.read_bytes()).decode("ascii")
        return f'src="data:{kind};base64,{data}"'
    return IMG_SRC.sub(swap, html)


def render_methods() -> str:
    """The rendered methods.html, from a throwaway copy of site/ and results/."""
    quarto = shutil.which("quarto")
    if quarto is None:
        raise SystemExit("quarto not found; run inside the whiplash env")
    work = Path(tempfile.mkdtemp(prefix="methods-"))
    try:
        for name in check_site.COPIED:
            shutil.copytree(ROOT / name, work / name,
                            ignore=shutil.ignore_patterns("_site", ".quarto"))
        result = subprocess.run([quarto, "render", "methods.qmd"], cwd=work / "site",
                                env=check_site._quarto_env(), capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        page = work / "site" / "_site" / "methods.html"
        if result.returncode != 0 or not page.exists():
            raise SystemExit(f"quarto render failed:\n{result.stderr[-2000:]}")
        return _inline_images(page.read_text("utf-8"), page.parent)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def wrap(rendered: str, commit: str) -> str:
    """One self-contained page from the rendered page's <main> element."""
    match = MAIN.search(rendered)
    if match is None:
        raise ValueError("No <main> element in the rendered methods page.")
    body = re.sub(r"<table\b", '<div class="tablewrap"><table', match.group(1))
    body = body.replace("</table>", "</table></div>")
    css = PAGE_CSS.replace("__FIGURE_GROUND__", theme.colour("surface"))
    return (f"<title>Whiplash Methods Draft</title>\n"
            f'<link rel="stylesheet" href="{theme.font_url()}">\n'
            f"<style>\n/* Layout: one reading column for prose; tables and the flowchart may run "
            f"wider inside their own scroll boxes. */\n{theme.css_variables()}\n{css}</style>\n"
            f'<div class="page"><div class="stamp">Reading copy of site/methods.qmd · commit '
            f"{commit} · numbers read from results/ at render</div>\n{body}\n</div>\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    args.out.write_bytes(wrap(render_methods(), commit).encode("utf-8"))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
