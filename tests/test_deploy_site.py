"""Tests for scripts/deploy_site.py: draft wording, host limits, the manifest.
No render, no git and no network."""
import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("deploy_site", ROOT / "scripts" / "deploy_site.py")
deploy_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy_site)


def test_draft_wording_is_found_in_visible_text_only():
    html = ('<p>Final text.</p><!-- DRAFT for the owner --><script>var draft = 1;</script>'
            '<style>.draft { color: red; }</style><div class="draft-note">Fine.</div>')
    assert deploy_site.draft_lines(html) == []
    html = '<div class="callout-title">Draft</div><p>*[Draft caption] December to February</p>'
    assert deploy_site.draft_lines(html) == ["Draft", "*[Draft caption] December to February"]
    assert deploy_site.draft_lines("<p>An updraft of warm air.</p>") == []


def test_draft_pages_names_each_page(tmp_path):
    (tmp_path / "index.html").write_text("<p>A first draft.</p>", encoding="utf-8")
    (tmp_path / "methods.html").write_text("<p>Settled.</p>", encoding="utf-8")
    assert deploy_site.draft_pages(tmp_path) == {"index.html": ["A first draft."]}


def test_limits_and_manifest(tmp_path, monkeypatch):
    (tmp_path / "sub").mkdir()
    (tmp_path / "index.html").write_bytes(b"<p>x</p>")
    (tmp_path / "sub" / "a.js").write_bytes(b"12345")
    assert deploy_site.limit_problems(tmp_path) == []
    monkeypatch.setattr(deploy_site, "FILE_LIMIT_BYTES", 6)
    assert deploy_site.limit_problems(tmp_path) == ["index.html: 8 bytes, over the 6 byte limit"]
    monkeypatch.setattr(deploy_site, "FILE_COUNT_LIMIT", 1)
    assert deploy_site.limit_problems(tmp_path)[-1] == "2 files, over the limit of 1"
    record = deploy_site.manifest(tmp_path, "abc1234", "2026-10-12T00:00:00Z")
    assert (record["commit"], record["n_files"], record["bytes"]) == ("abc1234", 2, 13)
    assert record["files"]["sub/a.js"] == {"bytes": 5, "sha256": hashlib.sha256(b"12345").hexdigest()}


def test_upload_is_not_configured_and_refuses_the_staging_flags(capsys):
    assert deploy_site.UPLOAD is None
    assert deploy_site.main(["--upload", "--allow-drafts"]) == 1
    assert "cannot be combined" in capsys.readouterr().out
