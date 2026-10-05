"""Tests for scripts/check_site.py: missing pages and broken local links."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_site", ROOT / "scripts" / "check_site.py")
check_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_site)


def test_local_links_skips_external_and_anchors():
    html = ('<a href="https://example.org/x">x</a><a href="#top">t</a>'
            '<a href="mailto:a@b.c">m</a><img src="fig%20a.svg"><a href="methods.html#h">m</a>')
    assert check_site.local_links(html) == ["fig a.svg", "methods.html"]


def test_missing_pages_finds_unrendered_qmd(tmp_path):
    site, out = tmp_path / "site", tmp_path / "site" / "_site"
    out.mkdir(parents=True)
    for name in ["index.qmd", "methods.qmd", "_draft.qmd"]:
        (site / name).write_text("", encoding="utf-8")
    (out / "index.html").write_text("", encoding="utf-8")
    # Pages starting with "_" are not rendered by Quarto, so not expected.
    assert check_site.missing_pages(site, out) == ["methods.qmd"]


def test_broken_links_catches_image_outside_site(tmp_path):
    # The 2026-10-04 failure: an image linked from ../results/ is not copied.
    out = tmp_path / "_site"
    (out / "index_files").mkdir(parents=True)
    (out / "index_files" / "ok.svg").write_text("<svg/>", encoding="utf-8")
    (out / "index.html").write_text(
        '<img src="index_files/ok.svg"><img src="../results/figures/mechanism.svg">',
        encoding="utf-8")
    assert check_site.broken_links(out) == ["index.html: ../results/figures/mechanism.svg"]
