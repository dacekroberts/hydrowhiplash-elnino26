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
    paths = banner.write(tmp_path)
    assert [p.name for p in paths] == [f"banner_{k}_{t}.png" for k, t in banner.BANNERS]
    for path, (kind, _) in zip(paths, banner.BANNERS):
        with Image.open(path) as image:
            assert image.size == banner.LAYOUTS[kind]["size"]


def test_banner_draws_only_the_seasons_the_tests_use():
    table = banner.seasons()
    assert set(table["region"]) == set(banner.ROWS)
    for region, g in table.groupby("region"):
        assert g["year"].max() == FIRE_LAST_YEAR_BY_REGION[region]
