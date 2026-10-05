"""Resolve merge conflicts in this project's two append-only logs.

DECISIONS.md and docs/plan_deviations.md only ever grow: both say "never edit
an old entry". Every side-session PR adds entries at the top of both, so when
two branches meet (a PR branch merging main in, merge-side-pr step 5) git
reports a conflict there. It is never a real disagreement, so this script
resolves it mechanically, and refuses whenever it can't be sure.

How: during a conflicted merge git keeps three versions of the file (stage 1
= merge base, 2 = ours, 3 = theirs). Each is parsed into its entry structure
and the three are merged entry by entry; git's conflict markers are ignored.
Rebuilding from the full versions means an entry git merged outside the
conflict markers can't be lost, and the result is checked to hold every
entry of both sides.

Structure, both files: preamble, "## " groups, "### " entries.
  DECISIONS.md             "## Changes" > "### YYYY-MM-DD - Topic" > "- **...**"
                           bullets. The bullet is the unit (one per decision),
                           so two branches adding bullets to one topic merge.
  docs/plan_deviations.md  "## YYYY-MM-DD (...)" > "### D<n> · Title". The whole
                           entry is the unit, and D numbers must stay unique.

Order: new items stay where their branch put them. Several new items in one
place are ordered newest first at the top of a list (by the date in the
heading, then the D number, then the time of the commit that added them) and
oldest first anywhere else (bullets appended to an existing topic).

Refuses (exit 1, nothing written) when: an existing entry was edited,
removed or moved on either side; both sides added the same heading with
different text, or the same D number for different entries; text outside
entries changed differently on both sides; a version's layout doesn't
round-trip (one blank line between blocks, except bullets in a list without
blank lines, which DECISIONS.md also uses; one newline at the end); or a new
entry can't be dated from git history.

Usage, inside a conflicted `git merge` (e.g. merge-side-pr's throwaway
worktree):
    python scripts/merge_append_only.py [FILE ...] [--dry-run]
With no FILE, resolves every conflicted file listed in LAYOUTS. Then review
with `git diff`, `git add` the files and commit the merge.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class Layout:
    split_bullets: bool       # each "- " bullet inside an entry is its own unit
    unique_id: str | None     # regex capturing an ID that must not repeat


LAYOUTS = {
    "DECISIONS.md": Layout(split_bullets=True, unique_id=None),
    "docs/plan_deviations.md": Layout(split_bullets=False, unique_id=r"^### (D\d+)\b"),
}

DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
DEVIATION_NO = re.compile(r"^### D(\d+)\b")


class Refusal(Exception):
    """The merge is not a pure append; a person has to resolve it."""


@dataclass
class Node:
    key: str                  # heading line, or the full text of a bullet
    text: str                 # own text: heading plus intro, or the whole leaf
    children: list[Node] = field(default_factory=list)
    leaf: bool = False
    # DECISIONS.md mixes both list styles: a bullet is "tight" when the next
    # bullet follows on the very next line rather than after a blank line.
    tight: bool = False
    side: int = 0             # during a merge: 0 base, 1 ours, 2 theirs


# Parsing and rendering

def parse(text: str, layout: Layout) -> Node:
    """Split a file into preamble, ## groups, ### entries and (optionally) bullets."""
    blocks: list[tuple[str, list[str]]] = [("pre", [])]
    in_entry = False
    for line in text.split("\n"):
        if line.startswith("## "):
            blocks.append(("h2", [line]))
            in_entry = False
        elif line.startswith("### "):
            blocks.append(("h3", [line]))
            in_entry = True
        elif layout.split_bullets and in_entry and line.startswith("- "):
            blocks.append(("bullet", [line]))
        else:
            blocks[-1][1].append(line)

    root = Node(key="", text="\n".join(blocks[0][1]).rstrip("\n"))
    group = entry = None
    for kind, lines in blocks[1:]:
        body = "\n".join(lines).rstrip("\n")
        if kind == "h2":
            group = Node(key=lines[0], text=body)
            root.children.append(group)
        elif kind == "h3":
            entry = Node(key=lines[0], text=body, leaf=not layout.split_bullets)
            (group or root).children.append(entry)
        else:
            entry.children.append(Node(key=body, text=body, leaf=True, tight=lines[-1] != ""))
    return root


def render(node: Node, top: bool = True) -> str:
    """Blocks joined by one blank line, or by a line break after a tight bullet."""
    out = node.text
    for i, child in enumerate(node.children):
        if out:
            out += "\n" if i and node.children[i - 1].tight else "\n\n"
        out += render(child, False)
    return out + "\n" if top else out


# Merging

@dataclass
class Context:
    when: Callable[[Node], int]     # commit time that introduced a new node
    where: str = ""


def _newness(node: Node, ctx: Context) -> tuple:
    first = node.key.split("\n", 1)[0]
    date = DATE.search(first)
    number = DEVIATION_NO.match(first)
    return (date.group(0) if date else "", int(number.group(1)) if number else -1,
            ctx.when(node))


def _short(key: str) -> str:
    return key.split("\n", 1)[0][:80]


def _merge_text(base: str, ours: str, theirs: str, where: str) -> str:
    if ours == theirs or theirs == base:
        return ours
    if ours == base:
        return theirs
    raise Refusal(f"{where}: text outside the entries changed differently on both "
                  f"sides; resolve by hand")


def _merge_existing(b: Node, o: Node, t: Node, ctx: Context) -> Node:
    where = f"{ctx.where} > {_short(b.key)}" if b.key else ctx.where
    if b.leaf:
        if o.text != b.text or t.text != b.text:
            side = "ours" if o.text != b.text else "theirs"
            raise Refusal(f"{where}: existing entry edited on {side}; old entries "
                          f"are never edited, so resolve by hand")
        return b
    sub = Context(ctx.when, where)
    return Node(b.key, _merge_text(b.text, o.text, t.text, where),
                _merge_lists(b.children, o.children, t.children, sub), b.leaf)


def _merge_new(o: Node, t: Node, ctx: Context) -> Node:
    """The same heading added on both sides."""
    where = f"{ctx.where} > {_short(o.key)}"
    if render(o, False) == render(t, False):
        return o
    if o.leaf or o.text != t.text:
        raise Refusal(f"{where}: added on both sides with different text; resolve by hand")
    return Node(o.key, o.text, _merge_lists([], o.children, t.children,
                                            Context(ctx.when, where)), o.leaf)


def _merge_lists(base: list[Node], ours: list[Node], theirs: list[Node],
                 ctx: Context) -> list[Node]:
    base_keys = [n.key for n in base]
    for side, nodes in (("ours", ours), ("theirs", theirs)):
        keys = [n.key for n in nodes]
        if len(set(keys)) != len(keys):
            raise Refusal(f"{ctx.where}: duplicate heading or entry on {side}")
        missing = [k for k in base_keys if k not in keys]
        if missing:
            raise Refusal(f"{ctx.where}: existing entry removed or edited on {side}: "
                          f"{_short(missing[0])!r}; old entries are never edited")
        if [k for k in keys if k in base_keys] != base_keys:
            raise Refusal(f"{ctx.where}: existing entries reordered on {side}")

    by = [{n.key: n for n in nodes} for nodes in (base, ours, theirs)]
    gaps: dict[int, list[Node]] = {i: [] for i in range(-1, len(base))}
    theirs_new = {n.key for n in theirs if n.key not in by[0]}
    for side, nodes in ((1, ours), (2, theirs)):
        gap = -1
        for n in nodes:
            if n.key in by[0]:
                gap = base_keys.index(n.key)
            elif side == 1 and n.key in theirs_new:
                gaps[gap].append(replace(_merge_new(n, by[2][n.key], ctx), side=1))
            elif side == 2 and n.key in by[1]:
                continue                       # already placed from ours
            else:
                gaps[gap].append(replace(n, side=side))

    out: list[Node] = []
    for gap in range(-1, len(base)):
        if gap >= 0:
            k = base_keys[gap]
            out.append(_merge_existing(by[0][k], by[1][k], by[2][k], ctx))
        # Newest first at the top of a list, oldest first when appended.
        out.extend(sorted(gaps[gap], key=lambda n: _newness(n, ctx), reverse=(gap == -1)))
    # An existing bullet followed by a new one keeps the spacing of the side
    # that added the new one (tight or blank-line list).
    for i in range(len(out) - 1):
        if out[i].key in by[0] and out[i + 1].side:
            out[i] = replace(out[i], tight=by[out[i + 1].side][out[i].key].tight)
    return out


def _leaves(node: Node, path: tuple = ()) -> set[tuple]:
    here = path + (node.key,)
    if node.leaf or not node.children:
        return {here}
    return set().union(*(_leaves(c, here) for c in node.children))


def merge_texts(base: str, ours: str, theirs: str, layout: Layout,
                when: Callable[[Node], int], name: str = "file") -> str:
    """Merge three versions of an append-only file; raise Refusal if unsafe."""
    trees = []
    for side, text in (("base", base), ("ours", ours), ("theirs", theirs)):
        tree = parse(text, layout)
        if render(tree) != text:
            raise Refusal(f"{name} ({side}): layout not recognised (blank lines between "
                          f"blocks or the final newline differ); resolve by hand")
        trees.append(tree)
    b, o, t = trees
    merged = Node("", _merge_text(b.text, o.text, t.text, name),
                  _merge_lists(b.children, o.children, t.children, Context(when, name)))

    if layout.unique_id:
        seen: dict[str, str] = {}
        for group in [merged] + merged.children:
            for entry in group.children:
                m = re.match(layout.unique_id, entry.key)
                if m and seen.setdefault(m.group(1), entry.key) != entry.key:
                    raise Refusal(f"{name}: {m.group(1)} is used by two entries "
                                  f"({_short(seen[m.group(1)])!r} and {_short(entry.key)!r}); "
                                  f"renumber the PR's entry and its pointers")

    if _leaves(merged) != _leaves(o) | _leaves(t):
        raise Refusal(f"{name}: result is not the union of both sides; resolve by hand")
    return render(merged)


# Git plumbing

def git(*args: str, cwd: Path) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    if out.returncode:
        raise Refusal(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def _dater(path: str, base: str, tips: tuple[str, str], cwd: Path) -> Callable[[Node], int]:
    cache: dict[str, int] = {}

    def when(node: Node) -> int:
        needle = node.key.split("\n", 1)[0]
        if needle not in cache:
            times = [int(t) for tip in tips for t in
                     git("log", "--format=%ct", "-S", needle, f"{base}..{tip}", "--",
                         path, cwd=cwd).split()]
            if not times:
                raise Refusal(f"{path}: can't date {needle[:60]!r} from git history; "
                              f"resolve by hand")
            cache[needle] = min(times)
        return cache[needle]
    return when


def resolve(path: str, top: Path, dry_run: bool) -> int:
    layout = LAYOUTS[path]
    base, ours, theirs = (git("show", f":{n}:{path}", cwd=top) for n in (1, 2, 3))
    head = git("rev-parse", "HEAD", cwd=top).strip()
    other = git("rev-parse", "MERGE_HEAD", cwd=top).strip()
    fork = git("merge-base", head, other, cwd=top).strip()
    result = merge_texts(base, ours, theirs, layout, _dater(path, fork, (head, other), top), path)
    added = len(_leaves(parse(result, layout))) - len(_leaves(parse(base, layout)))
    print(f"{path}: resolved; {added} entr{'y' if added == 1 else 'ies'} added on either "
          f"side since the branches split, all kept")
    if not dry_run:
        (top / path).write_text(result, encoding="utf-8", newline="\n")
    return added


def main(argv: list[str] | None = None, cwd: Path | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="files to resolve (default: every conflicted "
                                             "file in LAYOUTS)")
    ap.add_argument("--dry-run", action="store_true", help="check without writing")
    args = ap.parse_args(argv)
    try:
        top = Path(git("rev-parse", "--show-toplevel", cwd=cwd or Path.cwd()).strip())
        if not (Path(git("rev-parse", "--absolute-git-dir", cwd=top).strip()) / "MERGE_HEAD").exists():
            raise Refusal("not inside a conflicted git merge (no MERGE_HEAD)")
        conflicted = git("diff", "--name-only", "--diff-filter=U", cwd=top).split()
        files = [Path(f).as_posix() for f in args.files] or [f for f in conflicted if f in LAYOUTS]
        for f in files:
            if f not in LAYOUTS:
                raise Refusal(f"{f}: not an append-only file this script knows")
            if f not in conflicted:
                raise Refusal(f"{f}: not conflicted")
        for f in files:
            resolve(f, top, args.dry_run)
    except Refusal as err:
        print(f"REFUSED, nothing written: {err}")
        return 1
    others = [f for f in conflicted if f not in files]
    if not files:
        print("no conflicted append-only files")
    elif not args.dry_run:
        print(f"Next: review with `git diff`, then `git add {' '.join(files)}`")
    if others:
        print(f"still conflicted, resolve by hand: {', '.join(others)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
