"""Design tokens for the site, the private pages and the figures.

theme/tokens.json is the one source of every colour, typeface, spacing step
and radius (DECISIONS.md 2026-10-12 "Session 10: design system, hosting and
the map page"; D86). It has the shape of the Design System artifact's
project/tokens.json, so the artifact is a copy of this file. Nothing else
in the repository states a colour: figures read `colour()`, pages read the
CSS this module writes.

Run from the repo root:  python -m src.theme
writes site/theme/light.scss, dark.scss and fonts.html for the Quarto site.
tests/test_theme.py fails if those files no longer match the tokens.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "theme" / "tokens.json"
SITE_THEME = ROOT / "site" / "theme"
# The design typefaces, bundled with the site (owner, 2026-10-12) so no page
# depends on Google Fonts and matplotlib can draw with them. Variable fonts
# from github.com/google/fonts, SIL Open Font License 1.1 (OFL-*.txt beside
# them). (family, file, weight range, style). The private artifact pages
# cannot load these files and keep font_url().
SITE_FONTS_DIR = ROOT / "site" / "fonts"
SITE_FONTS = (
    ("National Park", "NationalPark-wght.ttf", "200 800", "normal"),
    ("Public Sans", "PublicSans-wght.ttf", "100 900", "normal"),
    ("Public Sans", "PublicSans-Italic-wght.ttf", "100 900", "italic"),
    ("JetBrains Mono", "JetBrainsMono-wght.ttf", "100 800", "normal"),
)
LENGTH_FAMILIES = ("spacing", "radius", "stroke")
# Text tokens and the grounds each must read on at 4.5:1 or better in every
# theme (WCAG 2); checked by tests/test_theme.py.
TEXT_ON = {
    "ink": ("page", "surface", "surface-sunk", "lichen", "fire-soft", "water-soft",
            "enso-soft"),
    "ink-muted": ("page", "surface", "surface-sunk"),
    "evergreen": ("page", "surface", "surface-sunk"),
    "on-evergreen": ("evergreen",),
}

# Rules of the Quarto site, appended to each theme's variables. They use the
# CSS variables only, so one set serves both themes. Figures are drawn on the
# light surface, so their panel keeps that ground in the dark theme too.
SITE_RULES = """
body { line-height: 1.62; }
main p, main li, main blockquote { max-width: 68ch; }
h1, h2, h3, h4, .navbar-brand, .navbar-nav { font-family: var(--font-display); text-wrap: balance; }
h1.title { font-size: 2.5rem; font-weight: 800; letter-spacing: -0.01em; line-height: 1.1; }
main h2 { font-size: 1.625rem; font-weight: 700; line-height: 1.2; margin-top: 3rem;
  padding: 1rem 0 0; border-bottom: 0; border-top: var(--stroke-mark) solid var(--evergreen); }
main h3 { font-size: 1.375rem; font-weight: 700; line-height: 1.3; margin-top: 1.9rem; }
main div.table-scroll { overflow-x: auto; max-width: 100%; margin-bottom: 1rem; }
main div.table-scroll > table { margin-bottom: 0; }
main div.table-scroll:focus-visible { outline: 2px solid var(--evergreen); outline-offset: 2px; }
body.fold-sections main h2 { cursor: pointer; display: flex; align-items: baseline;
  gap: 0.6rem; }
body.fold-sections main h2 .fold-toggle { flex: none; width: 1.5rem; height: 1.5rem; padding: 0;
  border: 1px solid var(--rule-strong); border-radius: var(--radius-md); background: var(--surface);
  color: var(--ink); cursor: pointer; font: 600 1rem/1 var(--font-sans); align-self: center; }
body.fold-sections main h2 .fold-toggle::before { content: "−"; }
body.fold-sections main section.folded > h2 .fold-toggle::before { content: "+"; }
body.fold-sections main section.folded > .fold-body { display: none; }
body.fold-sections main section.folded > h2 { color: var(--ink-muted); }
body.fold-sections p.fold-all { display: flex; gap: var(--space-2); margin: var(--space-4) 0 0;
  max-width: none; }
body.fold-sections p.fold-all button { font: inherit; font-size: 0.84rem; color: var(--ink);
  background: var(--surface); border: 1px solid var(--rule-strong); border-radius: var(--radius-md);
  padding: 2px 10px; cursor: pointer; }
code, pre, kbd { font-family: var(--font-mono); font-size: 0.86em; }
p code, li code, td code { background: var(--surface-sunk); color: var(--ink);
  padding: 1px 4px; border-radius: var(--radius-sm); }
a { text-decoration-color: var(--rule-strong); text-underline-offset: 2px; }
a:focus-visible { outline: var(--stroke-mark) solid var(--evergreen); outline-offset: 2px; }
blockquote { border-left: 3px solid var(--rule); color: var(--ink-muted); padding-left: 14px; }
main table, main .table { font-size: 0.86rem; background: var(--surface); color: var(--ink);
  border: 1px solid var(--rule); }
main .table > :not(caption) > * > * { background: none; color: inherit;
  border-bottom-color: var(--rule); padding: 6px 11px; }
main .table thead th { font-family: var(--font-sans); font-size: 0.72rem; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-muted);
  border-bottom: 1px solid var(--rule-strong); }
main td[style*="right"] { font-family: var(--font-mono); font-variant-numeric: tabular-nums;
  white-space: nowrap; }
main td strong { color: var(--evergreen); }
div.callout.callout-style-default { border: 0; border-top: var(--stroke-mark) solid var(--evergreen);
  border-radius: 0 0 var(--radius-md) var(--radius-md); background: var(--surface-sunk);
  color: var(--ink); max-width: 68ch; }
div.callout .callout-header { background: none; padding-bottom: 0; font-family: var(--font-sans);
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--ink-muted); }
div.callout .callout-icon-container { display: none; }
main .cell-output-display { background: __FIGURE_GROUND__; border: 1px solid var(--rule);
  border-radius: var(--radius-md); padding: var(--space-3); overflow-x: auto; }
/* A figure drawn once per theme: the pair sits in .fig-light and .fig-dark
   and the page shows the one matching its theme. */
body.quarto-dark main .fig-light, body:not(.quarto-dark) main .fig-dark { display: none; }
main .fig-dark .cell-output-display { background: var(--surface); }
main .cell-output-display svg, main .cell-output-display img { display: block; margin: 0 auto;
  max-width: 100%; height: auto; }
.navbar { border-bottom: 1px solid var(--rule); }
.navbar-brand { font-weight: 800; }
#TOC, .sidebar nav[role="doc-toc"] { font-size: 0.85rem; }
.sidebar nav[role="doc-toc"] ul > li > a.active { border-left-color: var(--evergreen);
  color: var(--evergreen) !important; }
.nav-footer { font-size: 0.84rem; color: var(--ink-muted); border-top: 1px solid var(--rule); }
ol.timetable { list-style: none; margin: var(--space-4) 0 0; padding: 0; background: var(--surface);
  border: 1px solid var(--rule); border-radius: var(--radius-md); }
ol.timetable > li { display: grid; grid-template-columns: 18px 9.5rem minmax(0, 1fr);
  gap: 2px var(--space-3); padding: 10px var(--space-4); border-bottom: 1px solid var(--rule);
  align-items: baseline; max-width: none; }
ol.timetable > li:last-child { border-bottom: 0; }
ol.timetable .st { width: 10px; height: 10px; border-radius: 50%; box-sizing: border-box;
  border: var(--stroke-mark) solid var(--rule-strong); align-self: center; }
ol.timetable .done .st { background: var(--moss); border-color: var(--moss); }
ol.timetable .next .st { border-color: var(--evergreen); box-shadow: 0 0 0 3px var(--lichen); }
ol.timetable .num { font-family: var(--font-mono); font-size: 0.8125rem;
  font-variant-numeric: tabular-nums; }
ol.timetable .what { font-weight: 600; }
ol.timetable .then { grid-column: 3; color: var(--ink-muted); font-size: 0.84rem; }
ol.timetable .chip { font-family: var(--font-sans); font-size: 0.72rem; font-weight: 600;
  letter-spacing: 0.06em; text-transform: uppercase; color: var(--evergreen); margin-left: 8px; }
ol.timetable li:not(.next) .chip { display: none; }
@media (max-width: 575px) { ol.timetable > li { grid-template-columns: 18px minmax(0, 1fr); }
  ol.timetable .what, ol.timetable .then { grid-column: 2; } }
div.overview { display: grid; grid-template-columns: repeat(auto-fit, minmax(13.5rem, 1fr));
  gap: var(--space-4) var(--space-6); margin-top: var(--space-4); margin-bottom: var(--space-6);
  padding: var(--space-4) 0 var(--space-2); border-top: var(--stroke-mark) solid var(--evergreen);
  border-bottom: 1px solid var(--rule); }
div.overview > div { min-width: 0; }
div.overview p.ov { font-family: var(--font-display); font-weight: 700; font-size: 1rem;
  margin: 0 0 var(--space-2); padding-bottom: var(--space-1); border-bottom: 1px solid var(--rule); }
div.overview ul { margin: 0; padding-left: 1.1rem; font-size: 0.92rem; }
div.overview li { margin-bottom: var(--space-2); max-width: none; }
div.overview i.sw { display: inline-block; width: 9px; height: 9px; border-radius: 50%;
  margin-right: 6px; background: var(--rule-strong); }
div.overview i.sw.fire { background: var(--fire); }
div.overview i.sw.water { background: var(--water); }
div.overview i.sw.snow { background: var(--snow); }
div.overview i.sw.temp { background: var(--temp-warm-2); }
div.overview i.sw.enso { background: var(--enso); }
div.rmap { margin-top: var(--space-4); }
div.rmap fieldset.rmap-layers { border: 0; padding: 0; margin: 0 0 var(--space-3); display: flex;
  flex-wrap: wrap; gap: var(--space-2); align-items: center; }
div.rmap fieldset.rmap-layers legend { float: left; width: auto; margin: 0 var(--space-2) 0 0;
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--ink-muted); }
div.rmap fieldset.rmap-layers label { cursor: pointer; }
div.rmap fieldset.rmap-layers input { position: absolute; opacity: 0; }
div.rmap fieldset.rmap-layers span { display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border: 1px solid var(--rule-strong); border-radius: var(--radius-pill);
  background: var(--surface); font-size: 0.9rem; }
div.rmap fieldset.rmap-layers span i { width: 9px; height: 9px; border-radius: 50%; }
div.rmap fieldset.rmap-layers input:checked + span { background: var(--evergreen);
  border-color: var(--evergreen); color: var(--on-evergreen); font-weight: 600; }
div.rmap fieldset.rmap-layers input:focus-visible + span { outline: 2px solid var(--evergreen);
  outline-offset: 2px; }
div.rmap .rmap-year { background: var(--surface); border: 1px solid var(--rule);
  border-radius: var(--radius-md); padding: var(--space-3) var(--space-4); }
div.rmap .rmap-step { display: flex; align-items: center; justify-content: center;
  gap: var(--space-2); flex-wrap: wrap; }
div.rmap .rmap-step button { font: inherit; font-size: 0.84rem; color: var(--ink);
  background: var(--surface-sunk); border: 1px solid var(--rule); border-radius: var(--radius-md);
  padding: 2px 10px; cursor: pointer; }
div.rmap .rmap-step button[data-nino] { border-color: var(--enso); }
div.rmap .rmap-y { font-family: var(--font-display); font-weight: 800; font-size: 1.75rem;
  font-variant-numeric: tabular-nums; min-width: 4.5ch; text-align: center; }
div.rmap .rmap-slide { position: relative; margin-top: var(--space-2); padding-bottom: 18px; }
div.rmap .rmap-slide input { width: 100%; accent-color: var(--evergreen); margin: 0; }
div.rmap .rmap-marks { position: absolute; left: 8px; right: 8px; bottom: 0; height: 14px; }
div.rmap .rmap-marks i { position: absolute; bottom: 0; height: 14px; transform: translateX(-50%);
  cursor: pointer; box-shadow: inset 0 0 0 1px var(--rule); }
div.rmap .rmap-marks i.neutral, div.rmap .rmap-key i.neutral { background: var(--enso-neutral); }
div.rmap .rmap-marks i.nino, div.rmap .rmap-key i.nino { background: var(--enso); }
div.rmap .rmap-marks i.strong, div.rmap .rmap-key i.strong { background: var(--enso-strong); }
div.rmap .rmap-marks i.nina, div.rmap .rmap-key i.nina { background: var(--enso-cold); }
div.rmap p.rmap-key { margin: 6px 0 0; max-width: none; font-size: 0.78rem; color: var(--ink-muted);
  display: flex; flex-wrap: wrap; align-items: center; gap: 4px 6px; }
div.rmap p.rmap-key i { width: 12px; height: 12px; border: 1px solid var(--rule-strong);
  margin-left: 8px; display: inline-block; }
div.rmap p.rmap-key i:first-child { margin-left: 0; }
div.rmap p.rmap-key span { margin-left: 10px; }
div.rmap p.rmap-when { margin: var(--space-2) 0 0; max-width: none; font-size: 0.9rem;
  display: flex; gap: var(--space-2); align-items: baseline; flex-wrap: wrap; }
div.rmap .rmap-chip { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; padding: 1px 8px; border-radius: var(--radius-pill);
  border: 1px solid var(--rule-strong); color: var(--ink-muted); }
div.rmap .rmap-chip.nino { background: var(--enso-soft); border-color: var(--enso);
  color: var(--ink); }
div.rmap .rmap-chip.strong { background: var(--enso); border-color: var(--enso-strong);
  color: var(--page); }
div.rmap .rmap-body { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
  gap: var(--space-4); margin-top: var(--space-4); align-items: start; }
div.rmap fieldset.rmap-sea-opts input:disabled + span { opacity: 0.45; cursor: default; }
div.rmap [hidden] { display: none !important; }
div.rmap .rmap-map { position: relative; background: var(--surface); overflow: hidden;
  border: 1px solid var(--rule); border-radius: var(--radius-md); }
div.rmap canvas { display: block; width: 100%; height: auto; }
div.rmap canvas.rmap-sea { position: absolute; inset: 0; height: 100%; }
div.rmap svg { width: 100%; height: auto; display: block; position: relative; }
div.rmap .rmap-ocean { margin: var(--space-4) 0; }
div.rmap .rmap-tropics { position: relative; margin: var(--space-2) 0; overflow: hidden;
  background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius-md); }
div.rmap .rmap-box { position: absolute; border: 1.5px solid var(--ink); pointer-events: none; }
div.rmap .rmap-box span { position: absolute; left: 0; bottom: 100%; font-size: 0.72rem;
  font-weight: 600; color: var(--ink); background: var(--surface); padding: 0 4px;
  white-space: nowrap; }
div.rmap ul.rmap-legend.rmap-sea-legend { display: flex; flex-wrap: wrap; gap: 4px 14px; }
div.rmap .rmap-sea-mini { margin: 0 0 var(--space-3); padding-top: var(--space-2);
  border-top: 1px solid var(--rule); font-size: 0.8rem; color: var(--ink-muted); }
div.rmap .rmap-sea-mini p { margin: 0 0 4px; max-width: none; font-size: 0.8rem; }
div.rmap .rmap-ramp { display: grid; grid-template-columns: repeat(5, 1fr); height: 12px;
  border: 1px solid var(--rule-strong); border-radius: var(--radius-sm); overflow: hidden; }
div.rmap p.rmap-ends { display: flex; justify-content: space-between; margin: 2px 0 0; }
div.rmap p.rmap-caution { margin: var(--space-3) 0 0; max-width: none; font-size: 0.9rem;
  padding: var(--space-3) var(--space-4); background: var(--surface);
  border: 1px solid var(--rule-strong); border-left: 4px solid var(--enso);
  border-radius: var(--radius-md); }
div.rmap svg path { fill: var(--surface-sunk); stroke: var(--page); stroke-width: 1.2;
  stroke-linejoin: round; fill-rule: evenodd; outline: none; }
div.rmap svg path.none { stroke: var(--rule-strong); stroke-dasharray: 3 3; }
div.rmap svg path.land { fill: var(--surface-sunk); stroke: var(--rule-strong); stroke-width: 0.6;
  pointer-events: none; }
div.rmap .rmap-tropics svg.rmap-land { position: absolute; inset: 0; height: 100%; }
div.rmap ul.rmap-legend i.land { background: var(--surface-sunk); }
div.rmap svg path.on, div.rmap svg path:focus-visible { stroke: var(--ink); stroke-width: 2.4; }
div.rmap svg text { font-family: var(--font-sans); font-size: 17px; font-weight: 600;
  fill: var(--ink); text-anchor: middle; dominant-baseline: middle; pointer-events: none;
  paint-order: stroke; stroke: var(--surface); stroke-width: 3.5px; stroke-linejoin: round; }
div.rmap p.rmap-title { font-family: var(--font-display); font-weight: 700; font-size: 1.125rem;
  margin: 0; }
div.rmap p.rmap-what { margin: 4px 0 var(--space-3); font-size: 0.86rem; color: var(--ink-muted);
  max-width: none; }
div.rmap ul.rmap-legend { list-style: none; margin: 0 0 var(--space-3); padding: 0;
  display: grid; gap: 3px; font-size: 0.84rem; }
div.rmap ul.rmap-legend li { display: flex; align-items: center; gap: 8px; max-width: none; }
div.rmap ul.rmap-legend i, div.rmap table.rmap-table .sw { width: 14px; height: 14px; flex: none;
  border-radius: var(--radius-sm); border: 1px solid var(--rule-strong); display: inline-block; }
div.rmap i.none, div.rmap .sw.none { background: var(--surface-sunk); border-style: dashed !important; }
div.rmap table.rmap-table { width: 100%; font-size: 0.84rem; border-top: 1px solid var(--rule); }
div.rmap table.rmap-table th, div.rmap table.rmap-table td { padding: 5px 4px;
  border-bottom: 1px solid var(--rule); vertical-align: top; text-transform: none;
  letter-spacing: 0; font-size: 0.84rem; color: var(--ink); white-space: normal; }
div.rmap table.rmap-table th { font-weight: 600; width: 44%; }
div.rmap table.rmap-table th .sw { margin-right: 8px; vertical-align: -2px; }
div.rmap table.rmap-table tr.on, div.rmap table.rmap-table tr:focus-visible {
  background: var(--surface-sunk); outline: none; }
@media (max-width: 767px) { div.rmap .rmap-body { grid-template-columns: 1fr; } }
div.waiting { display: grid; grid-template-columns: 9.5rem minmax(0, 1fr); gap: var(--space-3);
  align-items: baseline; padding: var(--space-3) var(--space-4); background: var(--surface);
  border: 1px dashed var(--rule-strong); border-radius: var(--radius-md); }
div.waiting p { margin: 0; max-width: none; }
div.waiting .num { font-family: var(--font-mono); font-size: 0.8125rem; }
@media (max-width: 575px) { div.waiting { grid-template-columns: 1fr; gap: 2px; } }
"""


def tokens() -> dict:
    return json.loads(TOKENS.read_text("utf-8"))


def themes() -> list[str]:
    return [t["id"] for t in tokens()["color"]["themes"]]


def colours(theme: str = "light") -> dict[str, str]:
    """Every colour token's value in one theme. A token with one value for
    all themes (the data ramps) returns that value; one missing a theme
    takes the first theme's, as the Design System page does."""
    ids = themes()
    if theme not in ids:
        raise ValueError(f"No theme {theme!r} in {TOKENS.name}; it holds {ids}.")
    out = {}
    for token in tokens()["color"]["tokens"]:
        value = token["value"]
        out[token["name"]] = value if isinstance(value, str) else value.get(theme, value[ids[0]])
    return out


def colour(name: str, theme: str = "light") -> str:
    """One colour token as a hex string. Figures are drawn in the light theme."""
    values = colours(theme)
    if name not in values:
        raise KeyError(f"No colour token {name!r} in {TOKENS.name}.")
    return values[name]


def lengths() -> dict[str, str]:
    """Spacing, radius and stroke tokens, by name."""
    data = tokens()
    return {t["name"]: t["value"] for family in LENGTH_FAMILIES for t in data[family]["tokens"]}


def families() -> dict[str, str]:
    """Font stacks by role: display, sans, mono."""
    return dict(tokens()["type"]["families"])


def font_url() -> str:
    return tokens()["meta"]["font_url"]


def contrast(a: str, b: str) -> float:
    """WCAG 2 contrast ratio of two #rrggbb colours."""
    def luminance(hex_colour: str) -> float:
        channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _declarations(values: dict[str, str]) -> str:
    return " ".join(f"--{name}: {value};" for name, value in values.items())


def _shared_declarations() -> str:
    fonts = {f"font-{key}": stack for key, stack in families().items()}
    return _declarations({**lengths(), **fonts})


def css_variables() -> str:
    """The tokens as CSS custom properties for a self-contained page: light
    values on :root, dark values for a dark system setting and again for an
    explicit dark choice, so a page toggle wins in both directions."""
    ids = themes()
    first = colours(ids[0])
    blocks = [f":root {{ {_declarations(first)} {_shared_declarations()} }}"]
    for theme in ids[1:]:
        changed = {k: v for k, v in colours(theme).items() if v != first[k]}
        dark = f"{_declarations(changed)} color-scheme: {theme};"
        blocks.append(f"@media (prefers-color-scheme: {theme}) {{ "
                      f":root:not([data-theme=\"{ids[0]}\"]) {{ {dark} }} }}")
        blocks.append(f":root[data-theme=\"{theme}\"] {{ {dark} }}")
    return "\n".join(blocks)


def quarto_scss(theme: str) -> str:
    """One Quarto theme file: Bootstrap variables from the tokens, then the
    tokens as CSS variables and the site's own rules."""
    c, fonts = colours(theme), families()
    defaults = {
        "body-bg": c["page"], "body-color": c["ink"], "link-color": c["evergreen"],
        "primary": c["evergreen"], "secondary": c["ink-muted"],
        "border-color": c["rule"], "code-bg": c["surface-sunk"], "code-color": c["ink"],
        "navbar-bg": c["page"], "navbar-fg": c["ink"], "navbar-hl": c["evergreen"],
        "footer-bg": c["page"], "footer-fg": c["ink-muted"],
        "font-family-sans-serif": fonts["sans"], "font-family-monospace": fonts["mono"],
        "headings-font-family": fonts["display"], "headings-color": c["ink"],
        "font-size-root": "16px", "border-radius": lengths()["radius-md"],
    }
    lines = ["// Generated from theme/tokens.json by python -m src.theme. Edit the tokens, "
             "not this file.", "/*-- scss:defaults --*/"]
    lines += [f"${name}: {value};" for name, value in defaults.items()]
    lines += ["/*-- scss:rules --*/", f":root {{ {_declarations(c)} {_shared_declarations()} }}",
              SITE_RULES.strip().replace("__FIGURE_GROUND__", colour("surface", themes()[0]))]
    return "\n".join(lines) + "\n"


def fonts_html() -> str:
    """@font-face rules for the site's bundled font files. Every page sits
    at the site root, so the relative address fonts/<file> resolves."""
    faces = [f'@font-face {{ font-family: "{family}"; src: url("fonts/{name}") '
             f'format("truetype"); font-weight: {weight}; font-style: {style}; '
             f'font-display: swap; }}' for family, name, weight, style in SITE_FONTS]
    return "<style>\n" + "\n".join(faces) + "\n</style>\n"


def site_files() -> dict[str, str]:
    """File name to text for everything written into site/theme/."""
    files = {f"{theme}.scss": quarto_scss(theme) for theme in themes()}
    files["fonts.html"] = fonts_html()
    return files


def write_site_theme(folder: Path = SITE_THEME) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, text in site_files().items():
        path = folder / name
        path.write_bytes(text.encode("utf-8"))  # LF on every platform
        paths.append(path)
    return paths


if __name__ == "__main__":
    for written in write_site_theme():
        print(written)
