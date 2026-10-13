"""Render the Quarto site and fail unless every page and every local link exists.

`quarto render` exits 0 in two silent failures seen on 2026-10-04: it renders
no pages at all when the project path contains a folder starting with "."
(e.g. a worktree under .claude/), and it leaves out images linked from
outside site/ (e.g. ../results/figures/), so the built page shows a broken
image. This script checks the output instead of the exit code.

The render runs on a copy of site/ and results/ in a short temporary folder,
so it works from any checkout (including worktrees), sidesteps the Windows
260-character path limit hit by Quarto's cache files, and never writes
site/_site/ into the repo. The copy is deleted on success and kept for
inspection on failure.

Run inside the whiplash env:  python scripts/check_site.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
COPIED = ["site", "results"]
LINK_ATTRS = {"src", "href"}


class _LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        self.links += [v for k, v in attrs if k in LINK_ATTRS and v]


def local_links(html: str) -> list[str]:
    """src and href values that point at files in the built site."""
    parser = _LinkCollector()
    parser.feed(html)
    out = []
    for link in parser.links:
        parts = urlsplit(link)
        if parts.scheme or parts.netloc or not parts.path:  # external, mailto, "#anchor"
            continue
        out.append(unquote(parts.path))
    return out


def missing_pages(site: Path, out: Path) -> list[str]:
    """Source pages with no rendered .html in the output folder."""
    pages = [p for p in site.rglob("*.qmd")
             if not any(part.startswith(("_", ".")) for part in p.relative_to(site).parts)]
    return [str(p.relative_to(site)) for p in pages
            if not (out / p.relative_to(site).with_suffix(".html")).exists()]


def broken_links(out: Path) -> list[str]:
    """Local src/href targets in the rendered HTML that don't exist on disk."""
    broken = []
    for page in out.rglob("*.html"):
        for link in local_links(page.read_text(encoding="utf-8")):
            target = (out / link.lstrip("/")) if link.startswith("/") else (page.parent / link)
            if not target.exists():
                broken.append(f"{page.relative_to(out)}: {link}")
    return broken


def _quarto_env() -> dict:
    """Environment for quarto, with the env's own Python and deno_dom."""
    env = dict(os.environ, QUARTO_PYTHON=sys.executable)
    # The conda-forge activation script can point QUARTO_DENO_DOM at the
    # package's build folder (D:/bld/...); fall back to the env's own copy.
    dom = Path(sys.prefix) / "Library" / "lib" / "deno_dom.dll"
    if not Path(env.get("QUARTO_DENO_DOM", "")).exists() and dom.exists():
        env["QUARTO_DENO_DOM"] = str(dom)
    return env


def render_copy() -> tuple[Path, Path, list[str]]:
    """Render a temporary copy of the site. Returns the temporary folder,
    the built site inside it and the problems found (empty when the build
    is whole). The caller removes the folder."""
    quarto = shutil.which("quarto")
    if quarto is None:
        return Path(), Path(), ["quarto not found; run inside the whiplash env"]
    work = Path(tempfile.mkdtemp(prefix="site-"))
    for name in COPIED:
        shutil.copytree(ROOT / name, work / name,
                        ignore=shutil.ignore_patterns("_site", ".quarto"))
    site = work / "site"
    result = subprocess.run([quarto, "render"], cwd=site, env=_quarto_env(),
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = site / "_site"
    problems = []
    if result.returncode != 0:
        problems.append(f"quarto render exited {result.returncode}:\n{result.stderr[-2000:]}")
    problems += [f"page not rendered: {p}" for p in missing_pages(site, out)]
    if out.exists():
        problems += [f"broken link: {b}" for b in broken_links(out)]
    return work, out, problems


def main() -> int:
    work, out, problems = render_copy()
    if problems:
        print("\n".join(problems))
        if work != Path():
            print(f"site check failed; rendered copy kept at {work}")
        return 1
    n_pages = len(list(out.rglob("*.html")))
    shutil.rmtree(work, ignore_errors=True)
    print(f"site OK: {n_pages} pages rendered, all local links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
