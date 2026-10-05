"""Tests for src/figures.py: site figures are written and reproducible."""
from src import figures
from src.config import REGIONS


def test_mechanism_writes_svg_and_png(tmp_path):
    paths = figures.mechanism_diagram(tmp_path)
    assert [p.name for p in paths] == ["mechanism.svg", "mechanism.png"]
    assert all(p.stat().st_size > 0 for p in paths)


def test_mechanism_svg_is_reproducible(tmp_path):
    # Byte-identical SVG between runs, so committed figures can be drift-checked.
    first = figures.mechanism_diagram(tmp_path / "a")[0].read_bytes()
    second = figures.mechanism_diagram(tmp_path / "b")[0].read_bytes()
    assert first == second


def test_mechanism_regions_match_config():
    # Every configured region is either drawn in a pathway or named in the footnote.
    drawn = figures.NORTH_REGIONS + figures.SOUTH_REGIONS
    assert set(drawn) <= set(REGIONS)
    assert set(drawn) | set(figures.UNDRAWN_REGIONS) == set(REGIONS)
    assert not set(drawn) & set(figures.UNDRAWN_REGIONS)
