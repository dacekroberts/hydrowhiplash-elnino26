"""Tests for src/figures.py: site figures are written and reproducible."""
from src import figures
from src.config import REGIONS


def test_mechanism_writes_both_layouts(tmp_path):
    paths = figures.mechanism_diagram(tmp_path)
    assert sorted(p.name for p in paths) == [
        "mechanism.png", "mechanism.svg", "mechanism_narrow.png", "mechanism_narrow.svg"]
    assert all(p.stat().st_size > 0 for p in paths)


def test_mechanism_svg_is_reproducible(tmp_path):
    # Byte-identical SVG between runs, so committed figures can be drift-checked.
    first = [p.read_bytes() for p in figures.mechanism_diagram(tmp_path / "a") if p.suffix == ".svg"]
    second = [p.read_bytes() for p in figures.mechanism_diagram(tmp_path / "b") if p.suffix == ".svg"]
    assert first == second


def test_mechanism_svg_has_lf_line_endings(tmp_path):
    # Git checks SVGs out with LF (.gitattributes); CRLF would fail a byte comparison.
    for p in figures.mechanism_diagram(tmp_path):
        if p.suffix == ".svg":
            assert b"\r\n" not in p.read_bytes()


def test_mechanism_regions_match_config():
    # Every configured region is either drawn in a pathway or named in the footnote.
    drawn = figures.NORTH_REGIONS + figures.SOUTH_REGIONS
    assert set(drawn) <= set(REGIONS)
    assert set(drawn) | set(figures.UNDRAWN_REGIONS) == set(REGIONS)
    assert not set(drawn) & set(figures.UNDRAWN_REGIONS)
