"""The sample visuals of session 12: the dashboard page and the banners."""
import json
import re
import sys
from pathlib import Path

import pandas as pd
from PIL import Image

from src import banner
from src.config import FIRE_LAST_YEAR_BY_REGION, ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import build_dashboard  # noqa: E402


def _payload(page: str) -> dict:
    text = re.search(r'<script type="application/json" id="data">(.*?)</script>', page, re.S)
    return json.loads(text.group(1).replace("<" + chr(92) + "/", "</"))


def test_dashboard_reads_the_run_and_holds_no_held_back_season():
    page = build_dashboard.build()
    assert "__" not in page.split("<script", 1)[0]
    data = _payload(page)
    reg = pd.read_csv(build_dashboard.TABLES / build_dashboard.RUN / "registered_tests.csv")
    assert data["counts"]["tests"] == len(reg)
    assert data["counts"]["significant"] == int((reg["significant"] == True).sum())  # noqa: E712
    assert len(data["survived"]) == data["counts"]["significant"]
    for region in data["regions"]:
        years = [s["year"] for s in region["seasons"]]
        assert max(years) == FIRE_LAST_YEAR_BY_REGION[region["region"]]


def test_dashboard_flow_uses_the_site_flowchart_labels():
    from src import diagrams
    flow = build_dashboard.flow()
    assert len(flow["sources"]) == len(diagrams.PROJECT_STREAMS)
    assert flow["sources"][0]["text"][0] == diagrams.PROJECT_STREAMS[0][0].split("\n")[0]


def test_wrap_keeps_every_word():
    for lines in (1, 2, 3):
        out = banner.wrap(banner.QUESTION, lines)
        assert len(out) == lines and " ".join(out) == banner.QUESTION


def test_banners_have_their_pixel_sizes(tmp_path: Path):
    paths = banner.write(tmp_path, preview=None)
    assert [p.name for p in paths] == [f"banner_{k}_{t}.png" for k, t in banner.BANNERS]
    for path, (kind, _) in zip(paths, banner.BANNERS):
        with Image.open(path) as image:
            assert image.size == banner.LAYOUTS[kind]["size"]


def test_site_preview_is_the_map_card_and_the_card_says_the_banner_line(tmp_path: Path):
    kind, _ = banner.SITE_PREVIEW[0]
    preview = tmp_path / "preview.png"
    paths = banner.write(tmp_path, preview=preview)
    assert paths[-1] == preview
    committed = banner.SITE_PREVIEW[1]
    for path in (preview, committed):
        with Image.open(path) as image:
            assert image.size == banner.LAYOUTS[kind]["size"]
    # The map card draws every region, each with a fill and a border or a
    # coast, and holds a credit for the map.
    shapes = json.loads(banner.map_page.CARD_OUT.read_text("utf-8"))
    assert set(shapes["regions"]) == set(banner.ROWS)
    for shape in shapes["regions"].values():
        assert shape["d"] and (shape["border"] or shape["coast"])
    assert set(banner.LABEL_SHIFT) | set(banner.LABEL_CALLOUT) <= set(banner.ROWS)
    assert "map" in banner.LAYOUTS[kind] and banner.MAP_CREDIT
    config = (committed.parent / "_quarto.yml").read_text("utf-8")
    assert f"image: {committed.name}" in config and f'- "{committed.name}"' in config
    # The card's description, on every page, is the banner's line.
    assert f'description: "{banner.QUESTION}"' in config


def test_banner_draws_only_the_seasons_the_tests_use():
    table = banner.seasons()
    assert set(table["region"]) == set(banner.ROWS)
    for region, g in table.groupby("region"):
        assert g["year"].max() == FIRE_LAST_YEAR_BY_REGION[region]


def test_motion_brief_fits_the_film_and_the_map_has_every_region():
    import build_motion_handoff as handoff
    from src.config import REGIONS

    lengths = [round(share * handoff.FILM["max_seconds"]) for share, _, _ in handoff.SCENES]
    assert sum(lengths) == handoff.FILM["max_seconds"] == 150
    page = handoff.brief(build_dashboard.payload())
    assert f"Total {sum(lengths)} s." in page and "4 of 52 tests" in page
    assert len(handoff.CARDS) == len(handoff.SCENES)
    assert "0 of the 25 tests that set El Ni\u00f1o against burned area are significant" in page
    assert all("{" not in line.format(**handoff.FILM) for line in handoff.PROMPT)
    shapes = handoff.map_shapes()
    assert list(shapes["regions"]) == list(REGIONS) and shapes["coast"].startswith("M")
    assert handoff.notices().startswith(handoff.NOTICES_HEADING)


def test_film_transcript_holds_every_card_and_motion_lines_after_theirs():
    import build_motion_handoff
    import prepare_film
    lines = prepare_film.transcript()
    added = [line for _, line in prepare_film.ADDED]
    cards = [line for line in lines if line not in added]
    assert len(cards) == len(build_motion_handoff.CARDS)
    for after, line in prepare_film.ADDED:
        assert lines[lines.index(line) - 1] in (cards[after], *added)
    for theme in prepare_film.THEMES:
        record = json.loads((prepare_film.OUT / f"film_{theme}.json").read_text("utf-8"))
        assert record["transcript"] == lines


def test_dashboard_typical_season_is_the_sites_whole_hectares():
    # Audit 2026-10-17 E4: rounded once, as the site's season chart prints it
    from src import figures, fire_figures, pin_inputs
    table = figures.season_anomaly(fire_figures.test_seasons(
        pin_inputs.load_input(build_dashboard.TABLES / "fire_region_year.csv")))
    for region in _payload(build_dashboard.build())["regions"]:
        g = table[(table["region"] == region["region"]) & table["anomaly"].notna()]
        site = f"{float(__import__('numpy').expm1(g['log_burn'].mean())):,.0f}"
        assert f"{region['typical']:,}" == site, region["region"]
