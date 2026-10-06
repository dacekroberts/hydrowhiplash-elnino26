"""Tests for scripts/check_no_em_dashes.py on a throwaway folder tree."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_no_em_dashes",
                                              ROOT / "scripts" / "check_no_em_dashes.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

DASH = chr(0x2014)


def notebook(cells):
    return json.dumps({"cells": [{"cell_type": kind, "source": source} for kind, source in cells],
                       "metadata": {}, "nbformat": 4, "nbformat_minor": 5})


def test_notebook_code_cells_are_scanned_and_markdown_is_exempt(tmp_path):
    (tmp_path / "notebooks").mkdir()
    (tmp_path / "notebooks" / "n.ipynb").write_text(notebook([
        ("markdown", [f"Prose {DASH} allowed\n"]),
        ("code", ["x = 1\n", f"# comment {DASH} not allowed\n"]),
        ("code", f"y = '{DASH}'"),                          # source as one string
    ]), encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "m.py").write_text(f"# {DASH}\n", encoding="utf-8")
    hits = check.find_hits(tmp_path)
    assert [h.split(": ")[0] for h in hits] == ["src/m.py:1", "notebooks/n.ipynb:cell 2:2",
                                                 "notebooks/n.ipynb:cell 3:1"]


def test_repository_is_clean():
    assert check.find_hits() == []
