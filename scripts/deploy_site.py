"""Build the site for publication: one procedure for every rolling update
(ACTION_PLAN "Rolling publication", D76; hosting on the owner's domain
through Cloudflare, D84).

Steps, each of which stops the run when it fails:
  1. The checkout is clean and its commit is on the remote, so a published
     site always corresponds to one pushed commit.
  2. The site renders whole (scripts/check_site.py: every page, every local
     link).
  3. No page still carries draft wording (the word "draft" in its text).
  4. The build fits the host's limits (FILE_LIMIT_BYTES, FILE_COUNT_LIMIT).
  5. The build is staged in dist/site/ with dist/deploy_manifest.json beside
     it: the commit, the time, and the size and sha256 of every file.
  6. Upload, only with `--upload`: a direct upload of dist/site/ to the
     Cloudflare Pages project PAGES_PROJECT with Cloudflare's `wrangler`
     (owner, 2026-10-12: a scoped API token, not a stored browser sign-in).
     It needs `wrangler` on the PATH and two environment variables the owner
     sets outside the repository and outside any chat:
       CLOUDFLARE_API_TOKEN   a token with the one permission
                              "Account, Cloudflare Pages, Edit"
       CLOUDFLARE_ACCOUNT_ID  the account's id
     Without all three the run stops before anything is sent. The token can
     publish to the Pages project and nothing else: no DNS, no file host.

Nothing under data/ is read or staged: the site reads only results/.

Run inside the whiplash env:
  python scripts/deploy_site.py                  steps 1 to 5
  python scripts/deploy_site.py --allow-drafts   stage a build that still has draft wording
  python scripts/deploy_site.py --allow-dirty    stage from an uncommitted or unpushed checkout
  python scripts/deploy_site.py --upload         steps 1 to 6 (refuses the two flags above)
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
STAGED = DIST / "site"
MANIFEST = DIST / "deploy_manifest.json"
# Cloudflare Pages limits as generally stated (not re-read for this script): 25 MiB a
# file, 20,000 files a site on the free plan. Read the current figures when UPLOAD is set.
FILE_LIMIT_BYTES = 25 * 1024 * 1024
FILE_COUNT_LIMIT = 20_000
# Where the site is published (owner, 2026-10-12); .dev is HTTPS only.
SITE_URL = "https://hydrowhiplash.dacekroberts.dev"
PAGES_PROJECT = "hydrowhiplash"
PAGES_BRANCH = "main"            # the project's production branch
UPLOAD_ENV = ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID")
DRAFT_WORD = re.compile(r"\bdraft", re.IGNORECASE)

_spec = importlib.util.spec_from_file_location("check_site", ROOT / "scripts" / "check_site.py")
check_site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_site)


class _Text(HTMLParser):
    """The text a reader sees: scripts, styles and comments left out."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def draft_lines(html: str) -> list[str]:
    """Pieces of a page's visible text that hold the word "draft"."""
    parser = _Text()
    parser.feed(html)
    return [" ".join(part.split())[:80] for part in parser.parts if DRAFT_WORD.search(part)]


def draft_pages(out: Path) -> dict[str, list[str]]:
    found = {}
    for page in sorted(out.rglob("*.html")):
        lines = draft_lines(page.read_text(encoding="utf-8"))
        if lines:
            found[page.relative_to(out).as_posix()] = lines
    return found


def limit_problems(out: Path) -> list[str]:
    files = [p for p in out.rglob("*") if p.is_file()]
    problems = [f"{p.relative_to(out).as_posix()}: {p.stat().st_size:,} bytes, over the "
                f"{FILE_LIMIT_BYTES:,} byte limit" for p in files if p.stat().st_size > FILE_LIMIT_BYTES]
    if len(files) > FILE_COUNT_LIMIT:
        problems.append(f"{len(files):,} files, over the limit of {FILE_COUNT_LIMIT:,}")
    return problems


def manifest(out: Path, commit: str, when: str) -> dict:
    files = {}
    for p in sorted(q for q in out.rglob("*") if q.is_file()):
        data = p.read_bytes()
        files[p.relative_to(out).as_posix()] = {"bytes": len(data),
                                                "sha256": hashlib.sha256(data).hexdigest()}
    return {"commit": commit, "built_utc": when, "n_files": len(files),
            "bytes": sum(f["bytes"] for f in files.values()), "files": files}


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8").stdout.strip()


def checkout_problems() -> list[str]:
    problems = []
    if _git("status", "--porcelain"):
        problems.append("the checkout has uncommitted changes")
    head = _git("rev-parse", "HEAD")
    if not _git("branch", "-r", "--contains", head):
        problems.append("the current commit is not on the remote")
    return problems


def upload_command(commit: str) -> tuple[list[str], list[str]]:
    """The upload as a list of arguments, and what is missing for it to run
    (an empty list when it can). The token is read by wrangler from the
    environment; it is never put on the command line or printed."""
    import os

    wrangler = shutil.which("wrangler")
    missing = [f"environment variable {name} is not set" for name in UPLOAD_ENV
               if not os.environ.get(name)]
    if wrangler is None:
        missing.append("wrangler is not on the PATH (npm install -g wrangler)")
    command = [wrangler or "wrangler", "pages", "deploy", str(STAGED),
               "--project-name", PAGES_PROJECT, "--branch", PAGES_BRANCH,
               "--commit-hash", commit, "--commit-dirty=false"]
    return command, missing


def main(args: list[str]) -> int:
    allow_drafts, allow_dirty, upload = (f in args for f in ("--allow-drafts", "--allow-dirty", "--upload"))
    if upload and (allow_drafts or allow_dirty):
        print("--upload cannot be combined with --allow-drafts or --allow-dirty")
        return 1
    problems = checkout_problems()
    if problems and not allow_dirty:
        print("\n".join(problems))
        print("commit and push first, or pass --allow-dirty to stage a build that is not for upload")
        return 1
    work, out, problems = check_site.render_copy()
    if problems:
        print("\n".join(problems))
        return 1
    drafts = draft_pages(out)
    for page, lines in drafts.items():
        print(f"draft wording on {page}: {len(lines)} place(s), first: {lines[0]!r}")
    problems = limit_problems(out)
    if drafts and not allow_drafts:
        problems.append(f"{len(drafts)} page(s) still carry draft wording; "
                        "pass --allow-drafts to stage them anyway")
    if problems:
        print("\n".join(problems))
        shutil.rmtree(work, ignore_errors=True)
        return 1
    if STAGED.exists():
        shutil.rmtree(STAGED)
    DIST.mkdir(exist_ok=True)
    shutil.copytree(out, STAGED)
    shutil.rmtree(work, ignore_errors=True)
    record = manifest(STAGED, _git("rev-parse", "HEAD"),
                      datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    record["draft_pages"] = sorted(drafts)
    record["clean_checkout"] = not allow_dirty
    MANIFEST.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"staged {record['n_files']} files, {record['bytes']:,} bytes, in {STAGED}")
    print(f"manifest: {MANIFEST} (commit {record['commit'][:7]})")
    if not upload:
        return 0
    command, missing = upload_command(record["commit"])
    if missing:
        print("\n".join(missing))
        print("Nothing was sent.")
        return 1
    print(f"uploading to the Pages project {PAGES_PROJECT} ({SITE_URL})")
    return subprocess.run(command, cwd=ROOT).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
