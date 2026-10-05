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

Order. New items stay where their branch put them, and each side's own order
is kept; where both sides added items at the same place, the two sequences
are interleaved:
  - groups and entries are newest first: by the date in the heading, then the
    D number; on a tie, ours goes above theirs. Run on a PR branch after
    merging main in (ours = the PR), so the PR's entries go above main's: the
    most recently merged PR ends on top, matching main's history;
  - bullets added at the top of a topic follow the same rule; bullets
    appended below existing ones go theirs first, then ours.
The result depends only on the three versions, not on commit times, so
merging main into a PR once (just before it merges) or after every merge
gives the same file.

Refuses (exit 1, nothing written) when: an existing entry was edited,
removed or moved on either side; both sides added the same heading with
different text, or the same D number for different entries; text outside
entries changed differently on both sides; or a version's layout doesn't
round-trip (one blank line between blocks, except bullets in a list without
blank lines, which DECISIONS.md also uses; one newline at the end).

Deviation numbers are given at merge. Side sessions never pick a D number:
they title a new entry "### D?a · Title" (then D?b, D?c, unique within the
PR) and write the same token wherever the entry is referenced (DECISIONS.md,
"[mid-project: D?a]" plan markers, code comments). Before the logs are
merged, each placeholder defined in the PR's deviations log gets the next
free number after the highest real one on either side, oldest entry first
(from the bottom of the newest-first log up, so the log stays in descending
order), and every reference is rewritten in the files the PR changes.
Refuses when a placeholder is defined twice, is referenced but never
defined, or is left anywhere in the merged tree. In Markdown prose, a
backslash before the question mark makes a literal mention (it renders as
D?a and is not a placeholder); the files in LITERAL_PLACEHOLDERS describe
the rule and are skipped. The main session numbers its own entries directly.

Run it after every merge, not only conflicted ones: git merges these files
cleanly whenever two branches' additions don't touch the same lines, and a
clean merge can still hold the same D number twice. Usage, on a PR branch
(e.g. merge-side-pr's throwaway worktree):
    git merge --no-commit --no-ff origin/main    # keeps even a clean merge open
    python scripts/merge_append_only.py --against origin/main [FILE ...] [--dry-run]
With no FILE, merges every file in LAYOUTS: conflicted ones from git's stages,
cleanly merged ones from the merge base, HEAD and MERGE_HEAD (checked, and
put in order). The line "numbered: D?a -> D40, ..." (or "numbered: none")
reports the numbers given; prescreen_prs.py reads it. Then review with
`git diff`, `git add` the files it names and commit the merge. When the
branch already contains origin/main, git opens no merge ("Already up to
date"); with --against the script then still numbers any placeholders (commit
the result as an ordinary commit), or exits 0 with "nothing to check" when
there are none. Without --against, or when the branch doesn't contain that
ref, a missing merge is refused: it means the merge step was skipped.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path


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
DEVIATIONS = "docs/plan_deviations.md"
# A deviation-number placeholder such as D?a. No match for a backslash before
# the "?", the Markdown way to mention the token literally.
PLACEHOLDER = re.compile(r"(?<!\w)D\?[a-z]+(?!\w)")
PLACEHOLDER_DEF = re.compile(r"^### (D\?[a-z]+)(?!\w)", re.M)
# Files that describe the placeholder rule, so their tokens are examples.
LITERAL_PLACEHOLDERS = (
    "scripts/merge_append_only.py", "scripts/prescreen_prs.py",
    "tests/test_merge_append_only.py", "tests/test_prescreen_prs.py",
    ".claude/skills/merge-side-pr/SKILL.md",
)


class Refusal(Exception):
    """The merge is not a pure append; a person has to resolve it."""


@dataclass
class Node:
    key: str                  # heading line, or the full text of a bullet
    text: str                 # own text: heading plus intro, or the whole leaf
    children: list[Node] = field(default_factory=list)
    leaf: bool = False
    bullet: bool = False
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
            entry.children.append(Node(key=body, text=body, leaf=True, bullet=True,
                                       tight=lines[-1] != ""))
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

def _rank(node: Node) -> tuple:
    """Newness from the heading: its date, then its D number."""
    first = node.key.split("\n", 1)[0]
    date, number = DATE.search(first), DEVIATION_NO.match(first)
    return (date.group(0) if date else "", int(number.group(1)) if number else -1)


def _interleave(ours: list[Node], theirs: list[Node], appended: bool) -> list[Node]:
    """Merge two sides' new items, keeping each side's own order."""
    if appended:                       # bullets added below existing ones
        return theirs + ours
    out, i, j = [], 0, 0
    while i < len(ours) and j < len(theirs):
        if _rank(ours[i]) >= _rank(theirs[j]):     # newest first; ties: ours on top
            out.append(ours[i]); i += 1
        else:
            out.append(theirs[j]); j += 1
    return out + ours[i:] + theirs[j:]


def _short(key: str) -> str:
    return key.split("\n", 1)[0][:80]


def _merge_text(base: str, ours: str, theirs: str, where: str) -> str:
    if ours == theirs or theirs == base:
        return ours
    if ours == base:
        return theirs
    raise Refusal(f"{where}: text outside the entries changed differently on both "
                  f"sides; resolve by hand")


def _merge_existing(b: Node, o: Node, t: Node, where: str) -> Node:
    here = f"{where} > {_short(b.key)}" if b.key else where
    if b.leaf:
        if o.text != b.text or t.text != b.text:
            side = "ours" if o.text != b.text else "theirs"
            raise Refusal(f"{here}: existing entry edited on {side}; old entries "
                          f"are never edited, so resolve by hand")
        return b
    return Node(b.key, _merge_text(b.text, o.text, t.text, here),
                _merge_lists(b.children, o.children, t.children, here), b.leaf)


def _merge_new(o: Node, t: Node, where: str) -> Node:
    """The same heading added on both sides."""
    here = f"{where} > {_short(o.key)}"
    if render(o, False) == render(t, False):
        return o
    if o.leaf or o.text != t.text:
        raise Refusal(f"{here}: added on both sides with different text; resolve by hand")
    return Node(o.key, o.text, _merge_lists([], o.children, t.children, here), o.leaf)


def _merge_lists(base: list[Node], ours: list[Node], theirs: list[Node],
                 where: str) -> list[Node]:
    base_keys = [n.key for n in base]
    for side, nodes in (("ours", ours), ("theirs", theirs)):
        keys = [n.key for n in nodes]
        if len(set(keys)) != len(keys):
            raise Refusal(f"{where}: duplicate heading or entry on {side}")
        missing = [k for k in base_keys if k not in keys]
        if missing:
            raise Refusal(f"{where}: existing entry removed or edited on {side}: "
                          f"{_short(missing[0])!r}; old entries are never edited")
        if [k for k in keys if k in base_keys] != base_keys:
            raise Refusal(f"{where}: existing entries reordered on {side}")

    by = [{n.key: n for n in nodes} for nodes in (base, ours, theirs)]
    # New items per side, grouped by the existing item they follow (-1 = top).
    gaps = {i: ([], []) for i in range(-1, len(base))}
    for side, nodes in ((1, ours), (2, theirs)):
        gap = -1
        for n in nodes:
            if n.key in by[0]:
                gap = base_keys.index(n.key)
            elif side == 1 and n.key in by[2]:
                gaps[gap][0].append(replace(_merge_new(n, by[2][n.key], where), side=1))
            elif side == 2 and n.key in by[1]:
                continue                       # added on both sides; placed from ours
            else:
                gaps[gap][side - 1].append(replace(n, side=side))

    out: list[Node] = []
    for gap in range(-1, len(base)):
        if gap >= 0:
            k = base_keys[gap]
            out.append(_merge_existing(by[0][k], by[1][k], by[2][k], where))
        new_ours, new_theirs = gaps[gap]
        appended = gap >= 0 and any(n.bullet for n in new_ours + new_theirs)
        out.extend(_interleave(new_ours, new_theirs, appended))
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


def merge_texts(base: str, ours: str, theirs: str, layout: Layout, name: str = "file") -> str:
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
                  _merge_lists(b.children, o.children, t.children, name))

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


# Deviation placeholders

def highest_number(*texts: str | None) -> int:
    """The highest real D number in the given deviation logs (0 if none)."""
    return max((int(m.group(1)) for t in texts if t
                for m in re.finditer(r"^### D(\d+)\b", t, re.M)), default=0)


def number_placeholders(deviations: str, highest: int) -> dict[str, str]:
    """Placeholder -> real number, oldest entry first (bottom of the log up)."""
    defined = PLACEHOLDER_DEF.findall(deviations)
    twice = sorted({p for p in defined if defined.count(p) > 1})
    if twice:
        raise Refusal(f"{DEVIATIONS}: placeholder {', '.join(twice)} defined by two "
                      f"entries; give each new entry its own letter")
    return {p: f"D{highest + i}" for i, p in enumerate(reversed(defined), 1)}


def apply_numbers(text: str, numbers: dict[str, str]) -> str:
    return PLACEHOLDER.sub(lambda m: numbers.get(m.group(0), m.group(0)), text)


def _read_text(path: Path) -> str | None:
    """A file's text with its line endings as stored; None if binary or missing."""
    try:
        return path.read_bytes().decode("utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def number_tree(top: Path, revs: tuple[str, str, str]
                ) -> tuple[dict[str, str], dict[str, str], set[str]]:
    """Number the PR's placeholders.

    revs is (merge base, PR side, main side). Returns the numbers, the
    rewritten text of each other file the PR changes (the two logs are
    numbered in resolve), and the set of files the PR changes.
    """
    base, head, other = revs
    ours, theirs = (_show(rev, DEVIATIONS, top) for rev in (head, other))
    numbers = number_placeholders(ours or "", highest_number(ours, theirs))
    pr_files = set(git("diff", "--name-only", "--no-renames", base, head, cwd=top).split())
    rewritten = {}
    for f in sorted(pr_files):
        if f in LAYOUTS or f in LITERAL_PLACEHOLDERS:
            continue
        text = _read_text(top / f)
        if text is not None and apply_numbers(text, numbers) != text:
            rewritten[f] = apply_numbers(text, numbers)
    return numbers, rewritten, pr_files


def check_no_placeholders(top: Path, texts: dict[str, str], pr_files: set[str]) -> None:
    """Refuse if a placeholder is left in any tracked file (texts override disk)."""
    for f in sorted(set(git("ls-files", cwd=top).split())):
        if f in LITERAL_PLACEHOLDERS:
            continue
        found = PLACEHOLDER.search(texts[f] if f in texts else _read_text(top / f) or "")
        if not found:
            continue
        if f in pr_files:
            raise Refusal(f"{f}: {found.group(0)} is referenced but no entry in "
                          f"{DEVIATIONS} defines it; add the entry or fix the reference")
        raise Refusal(f"{f}: placeholder {found.group(0)} left in the merged tree, "
                      f"not from this PR; number it by hand")


# Git plumbing

def git(*args: str, cwd: Path) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    if out.returncode:
        raise Refusal(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def _show(rev: str, path: str, top: Path) -> str | None:
    out = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=top, capture_output=True,
                         text=True, encoding="utf-8", errors="replace")
    return out.stdout if out.returncode == 0 else None


def resolve(path: str, top: Path, conflicted: bool,
            revs: tuple[str, str, str], numbers: dict[str, str] | None = None) -> str | None:
    """Merge one file from its three versions; return the result (None if skipped).

    A conflicted file is read from git's stages; a file git merged cleanly is
    read from the merge base, HEAD and MERGE_HEAD, so its result is checked
    (unique D numbers, no edited entries, every entry kept) and put in order
    too. A clean merge can't be trusted alone: two branches adding D19 at
    different lines merge without a conflict. Placeholders on the PR side
    (ours) are numbered first.
    """
    layout = LAYOUTS[path]
    if conflicted:
        versions = [git("show", f":{n}:{path}", cwd=top) for n in (1, 2, 3)]
    else:
        versions = [_show(rev, path, top) for rev in revs]
        if None in versions:
            print(f"{path}: skipped, not in all three versions")
            return None
    if numbers:
        versions[1] = apply_numbers(versions[1], numbers)
    base = versions[0]
    result = merge_texts(*versions, layout, path)
    current = (top / path).read_text(encoding="utf-8")
    added = len(_leaves(parse(result, layout))) - len(_leaves(parse(base, layout)))
    changes = "numbered" if numbers and PLACEHOLDER.search(current) else "reordered"
    what = "resolved" if conflicted else (f"checked and {changes}" if result != current
                                           else "checked")
    print(f"{path}: {what}; {added} entr{'y' if added == 1 else 'ies'} added on either "
          f"side since the branches split, all kept")
    return result


def main(argv: list[str] | None = None, cwd: Path | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="files to merge (default: every file in "
                                             "LAYOUTS present in the working tree)")
    ap.add_argument("--dry-run", action="store_true", help="check without writing")
    ap.add_argument("--against", metavar="REF",
                    help="the branch that was merged in (e.g. origin/main): with no merge "
                         "open and HEAD already containing it, only number placeholders "
                         "(exit 0 with nothing to check if there are none)")
    args = ap.parse_args(argv)
    try:
        top = Path(git("rev-parse", "--show-toplevel", cwd=cwd or Path.cwd()).strip())
        head = git("rev-parse", "HEAD", cwd=top).strip()
        if (Path(git("rev-parse", "--absolute-git-dir", cwd=top).strip()) / "MERGE_HEAD").exists():
            other = git("rev-parse", "MERGE_HEAD", cwd=top).strip()
            revs = (git("merge-base", head, other, cwd=top).strip(), head, other)
        elif args.against and subprocess.run(
                ["git", "merge-base", "--is-ancestor", args.against, "HEAD"],
                cwd=top, capture_output=True).returncode == 0:
            # `git merge` opens no merge when the branch already contains the
            # other side ("Already up to date"): no clash is possible, but the
            # PR's placeholders still need numbers.
            other = git("rev-parse", args.against, cwd=top).strip()
            revs = (other, head, other)
        else:
            raise Refusal("not inside an open git merge (no MERGE_HEAD); merge with "
                          "`git merge --no-commit --no-ff` so clean merges stay open too")
        numbers, rewritten, pr_files = number_tree(top, revs)
        if revs[0] == revs[2] and not numbers:
            check_no_placeholders(top, {}, pr_files)
            print(f"nothing to check: no merge open, HEAD already contains {args.against}")
            print("numbered: none")
            return 0
        conflicted = git("diff", "--name-only", "--diff-filter=U", cwd=top).split()
        files = ([Path(f).as_posix() for f in args.files]
                 or [f for f in LAYOUTS if (top / f).exists()])
        for f in files:
            if f not in LAYOUTS:
                raise Refusal(f"{f}: not an append-only file this script knows")
        if numbers and DEVIATIONS not in files:
            files.append(DEVIATIONS)                 # the placeholders are defined there
        # Every file is merged before any is written, so a refusal writes nothing.
        results = {f: resolve(f, top, f in conflicted, revs, numbers) for f in files}
        check_no_placeholders(top, {**rewritten, **{f: t for f, t in results.items()
                                                     if t is not None}}, pr_files)
    except Refusal as err:
        print(f"REFUSED, nothing written: {err}")
        return 1
    print("numbered: " + (", ".join(f"{p} -> {n}" for p, n in numbers.items()) or "none"))
    changed = [f for f, text in results.items()
               if text is not None and text != (top / f).read_text(encoding="utf-8")]
    if not args.dry_run:
        for f in changed:
            (top / f).write_text(results[f], encoding="utf-8", newline="\n")
        for f, text in rewritten.items():
            (top / f).write_bytes(text.encode("utf-8"))        # line endings as stored
    to_add = sorted(set(changed) | set(rewritten) | {f for f in files if f in conflicted})
    if to_add and not args.dry_run:
        then = "" if revs[0] != revs[2] else " and commit (no merge is open)"
        print(f"Next: review with `git diff`, then `git add {' '.join(to_add)}`{then}")
    others = [f for f in conflicted if f not in files]
    if others:
        print(f"still conflicted, resolve by hand: {', '.join(others)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
