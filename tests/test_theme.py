"""Tests for src/theme.py: the tokens are well formed, legible, and the site's theme files are current."""
import re

import pytest

from src import theme

HEX = re.compile(r"^#[0-9a-f]{6}$")


def test_every_colour_is_a_hex_value_in_every_theme():
    for name in theme.themes():
        values = theme.colours(name)
        assert values, name
        for token, value in values.items():
            assert HEX.match(value), (name, token, value)


def test_token_names_are_unique_across_families():
    data = theme.tokens()
    names = [t["name"] for t in data["color"]["tokens"]]
    names += [t["name"] for family in theme.LENGTH_FAMILIES for t in data[family]["tokens"]]
    assert len(names) == len(set(names))


def test_text_tokens_reach_contrast_on_their_grounds():
    # WCAG 2 body-text floor, in every theme.
    for name in theme.themes():
        values = theme.colours(name)
        for text, grounds in theme.TEXT_ON.items():
            for ground in grounds:
                ratio = theme.contrast(values[text], values[ground])
                assert ratio >= 4.5, (name, text, ground, round(ratio, 2))


def test_fire_and_water_differ_in_lightness():
    # The data pair must not rest on hue alone.
    for name in theme.themes():
        values = theme.colours(name)
        assert theme.contrast(values["fire"], values["water"]) >= 1.25, name


def test_contrast_of_black_on_white():
    assert theme.contrast("#000000", "#ffffff") == pytest.approx(21.0)


def test_unknown_names_raise():
    with pytest.raises(KeyError):
        theme.colour("no-such-token")
    with pytest.raises(ValueError):
        theme.colours("sepia")


def test_css_variables_cover_both_theme_states():
    css = theme.css_variables()
    assert css.startswith(":root {")
    assert "--page: " + theme.colour("page") in css
    assert '@media (prefers-color-scheme: dark) { :root:not([data-theme="light"])' in css
    assert ':root[data-theme="dark"]' in css
    assert "--font-display:" in css and "--radius-md:" in css


def test_committed_site_theme_matches_the_tokens():
    # Fails when theme/tokens.json or the site rules change without a rewrite.
    # Fix: python -m src.theme, commit site/theme/.
    for name, text in theme.site_files().items():
        committed = theme.SITE_THEME / name
        assert committed.exists(), f"{committed} missing: run python -m src.theme"
        assert committed.read_bytes() == text.encode("utf-8"), (
            f"{name} is stale: run python -m src.theme and commit site/theme/")
