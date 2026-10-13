"""Tests for src/diagrams.py: site diagrams are written, reproducible and current."""
import pytest

from src import diagrams
from src.config import REGIONS


def test_mechanism_writes_both_layouts(tmp_path):
    paths = diagrams.mechanism_diagram(tmp_path)
    # each layout once per theme: the first theme keeps the stem
    assert sorted(p.name for p in paths) == sorted(
        f"mechanism{layout}{theme}.{ext}" for layout in ("", "_narrow")
        for theme in ("", "_dark") for ext in ("png", "svg"))
    assert all(p.stat().st_size > 0 for p in paths)


def test_mechanism_svg_is_reproducible(tmp_path):
    # Byte-identical SVG between runs, so committed figures can be drift-checked.
    first = [p.read_bytes() for p in diagrams.mechanism_diagram(tmp_path / "a") if p.suffix == ".svg"]
    second = [p.read_bytes() for p in diagrams.mechanism_diagram(tmp_path / "b") if p.suffix == ".svg"]
    assert first == second


def test_mechanism_svg_has_lf_line_endings(tmp_path):
    # Git checks SVGs out with LF (.gitattributes); CRLF would fail a byte comparison.
    for p in diagrams.mechanism_diagram(tmp_path):
        if p.suffix == ".svg":
            assert b"\r\n" not in p.read_bytes()


def test_committed_svgs_match_the_code(tmp_path):
    # Fails when src/diagrams.py or src/config.py (e.g. a new region) changes
    # without re-rendering. Fix: python -m src.diagrams, commit results/figures/.
    for diagram in diagrams.DIAGRAMS:
        for p in diagram(tmp_path):
            if p.suffix == ".svg":
                committed = diagrams.FIGURES / p.name
                assert committed.exists(), f"{committed} missing: run python -m src.diagrams"
                assert committed.read_bytes() == p.read_bytes(), (
                    f"{committed.name} is stale: run python -m src.diagrams and commit "
                    f"results/figures/")


def test_flowchart_writes_both_layouts(tmp_path):
    paths = diagrams.methods_flowchart(tmp_path)
    # each layout once per theme: the first theme keeps the stem
    assert sorted(p.name for p in paths) == sorted(
        f"methods_flow{layout}{theme}.{ext}" for layout in ("", "_narrow")
        for theme in ("", "_dark") for ext in ("png", "svg"))
    assert all(p.stat().st_size > 0 for p in paths)


def test_flowchart_svg_is_reproducible_with_lf(tmp_path):
    first = [p.read_bytes() for p in diagrams.methods_flowchart(tmp_path / "a") if p.suffix == ".svg"]
    second = [p.read_bytes() for p in diagrams.methods_flowchart(tmp_path / "b") if p.suffix == ".svg"]
    assert first == second
    assert all(b"\r\n" not in svg for svg in first)


def test_flowchart_names_every_decided_source_and_variable():
    # DECISIONS.md 2026-10-08 "Site methods flowchart" lists what the chart shows.
    text = " | ".join(diagrams.flow_labels())
    for name in ("ERA5-Land", "Snow stations", "MTBS", "WFIGS", "CNFDB", "ONI", "RONI",
                 "NBAC", "Winter precipitation", "Whiplash", "Snowpack", "Burned area",
                 "year table", "Pre-registered tests", "Site charts"):
        assert name in text, name


def test_flowchart_note_wording():
    # Owner-approved wording (2026-10-11); a change here needs the owner.
    assert diagrams.FLOW_NOTES == (
        "Arrows show groups, not single sources.",
        "Snow stations are used only to check the ERA5-Land snowpack.")
    assert diagrams.flow_labels()[-2:] == list(diagrams.FLOW_NOTES)


def test_flowchart_labels_carry_no_numbers():
    # Structure only: no result, estimate or data value. The one digit allowed
    # is in the dataset name ERA5-Land.
    for label in diagrams.flow_labels():
        assert not any(ch.isdigit() for ch in label.replace("ERA5-Land", "")), label


def test_mechanism_regions_match_config():
    # Every configured region is either drawn in a pathway or named in the footnote.
    drawn = diagrams.NORTH_REGIONS + diagrams.SOUTH_REGIONS
    assert set(drawn) <= set(REGIONS)
    assert set(drawn) | set(diagrams.UNDRAWN_REGIONS) == set(REGIONS)
    assert not set(drawn) & set(diagrams.UNDRAWN_REGIONS)


def test_footnote_names_every_undrawn_region_by_role(monkeypatch):
    regions = {"PNW": "primary", "AK": "north", "YT": "north", "NorCal": "contrast",
               "SoCal": "contrast"}
    monkeypatch.setattr(diagrams, "REGIONS", regions)
    monkeypatch.setattr(diagrams, "UNDRAWN_REGIONS", ("AK", "YT", "NorCal"))
    assert diagrams.footer_lines() == [
        "Expected pathways, tested in this study.",
        "AK and YT are also analysed, as northern regions; no pathway is drawn for "
        "them because their hypotheses are not yet set.",
        "NorCal is also analysed, as a contrast region; no pathway is drawn for it "
        "because its expected response is not yet set.",
    ]


def test_new_region_role_needs_wording(monkeypatch):
    monkeypatch.setattr(diagrams, "REGIONS", {"XX": "arctic"})
    monkeypatch.setattr(diagrams, "UNDRAWN_REGIONS", ("XX",))
    with pytest.raises(ValueError, match="No footnote wording"):
        diagrams.footer_lines()


def test_series_legend_reads_thresholds_from_config(monkeypatch):
    import matplotlib.pyplot as plt

    from src import figures
    monkeypatch.setattr(figures, "EL_NINO_THRESHOLD", 0.7)
    monkeypatch.setattr(figures, "STRONG_THRESHOLD", 1.8)
    fig = plt.figure()
    figures._legend(fig, "ONI")
    labels = [t.get_text() for t in fig.legends[0].get_texts()]
    plt.close(fig)
    assert "El Niño (DJF ONI ≥ 0.7): band and tick" in labels
    assert "Strong El Niño (≥ 1.8): darker tick, labelled" in labels
