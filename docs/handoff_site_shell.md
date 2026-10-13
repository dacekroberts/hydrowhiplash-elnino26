# Handoff: a neutral site shell for the prediction project

From hydrowhiplash-elnino26 (Session 11, 2026-10-12) to
climate-whiplash-prediction, for whenever that project publishes. It is
an offer, not a requirement: that project may decide it needs a different
shell. It holds no data, no results, no held-back seasons and no secrets.

## The three names

The "shell" is three layers, and two start with P:

| Layer | Tool | What it does |
|---|---|---|
| Site builder | **Quarto** | turns `.qmd` pages into a static website |
| Charts | **Plotly** | the interactive charts; plotly.js is served from the site itself |
| Host | **Cloudflare Pages** | serves the built folder at a subdomain of dacekroberts.dev |

## When this shell fits, and when it does not

It fits a site whose pages are built ahead of time from committed tables
and figures. It does not fit a page that must run Python while the reader
waits (a model that takes the reader's inputs and recomputes). That needs
an app host such as Streamlit, which is a different shell with different
rules. A precomputed forecast with sliders drawn in the browser still
fits this one.

## Layout

```
site/
  _quarto.yml        site title, navbar, footer, theme, header includes
  _rights.html       three rights meta tags, put in every page's head
  robots.txt         AI-training crawlers asked to stay out; search allowed
  index.qmd          one .qmd per page
  theme/             light.scss, dark.scss, fonts.html: generated, not hand-edited
  fonts/             font files served from the site
  libs/plotly.min.js plotly.js served from the site
theme/tokens.json    the colours, type sizes and spacing: the one place to edit
src/theme.py         writes site/theme/ from tokens.json
scripts/check_site.py    renders a copy; checks every page and local link
scripts/deploy_site.py   the publication gate and the upload
.claude/skills/deploy-site/SKILL.md   the procedure, with the traps
.claude/launch.json  a local preview server for the built site
dist/                staged build and manifest; ignored by git
```

## `_quarto.yml`, with the project's own parts blanked

```yaml
project:
  type: website
  output-dir: _site
  resources:
    - "fonts/*"
    - "libs/*"
    - "robots.txt"

website:
  title: "<SITE TITLE>"
  site-url: "https://<SUBDOMAIN>.dacekroberts.dev"
  page-footer: "Text and figures © <YEAR> Dace Roberts, all rights reserved. Code: MIT licence."
  navbar:
    left:
      - href: index.qmd
        text: Overview
      - href: methods.qmd
        text: Methods and limitations

author: "Dace Roberts"

format:
  html:
    theme:
      light: theme/light.scss
      dark: theme/dark.scss
    respect-user-color-scheme: true
    include-in-header:
      - theme/fonts.html
      - _rights.html
    toc: true
```

The footer line assumes the same split licence as this project (code MIT,
writing and figures all rights reserved). Change it if that project's
licences differ.

## Rules the shell enforces

1. **The site reads only `results/`.** Code writes figures and tables
   there; no page reads `data/`, and no number is typed by hand (Quarto
   inline Python reads it from a table).
2. **No request to any other host.** Fonts and plotly.js are served from
   the site (`include_plotlyjs=False` in the chart code, one
   `<script src="libs/plotly.min.js">` on the page).
3. **Rights in four places:** the footer line, the meta tags in
   `_rights.html`, a credit line inside each figure
   (`© <YEAR> Dace Roberts · <site address>`), and `robots.txt`.
4. **Credits for every data source** on the methods page, checked against
   the licence ledger before each publication. A map carries its credit
   wherever it appears.
5. **The publication gate** (`scripts/deploy_site.py`), each step stopping
   the run:
   1. the checkout is clean and its commit is pushed;
   2. every page renders and every local link resolves;
   3. no page's visible text holds the word "draft" ("work in progress" is
      allowed);
   4. no file over 25 MiB, no more than 20,000 files (Cloudflare's limits
      as generally stated; read the current figures before relying on them);
   5. the build is staged in `dist/site/` with a manifest: commit, time,
      size and sha256 of every file;
   6. with `--upload` only: `wrangler pages deploy dist/site
      --project-name <PROJECT> --branch main --commit-hash <commit>`.
6. **Every upload is asked for.** An earlier yes does not carry over.

## What the owner does once, in Cloudflare

1. Pick the subdomain and the Pages project name.
2. Create a scoped API token with the one permission "Account, Cloudflare
   Pages, Edit", and save it and the account id as the environment
   variables `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. Never in
   the repository, never in a chat. The existing token is account-wide for
   Pages, so the owner may reuse it or make a second one.
3. Restart the desktop app so sessions can see the variables.
4. After the first upload: add the custom domain to the Pages project in
   the dashboard (the token cannot touch DNS).

## Traps met here

- wrangler 4 hands `pages project create` to Workers hosting unless
  `--force` is given. Needed once, at creation only.
- Cloudflare adds an analytics script (Real User Measurements) to proxied
  domains on the Free plan by default. The owner switched it off for
  dacekroberts.dev on 2026-10-12, which should cover new subdomains, but
  check each new address in a real browser: the script is added only to
  document loads, so `curl` and `fetch` do not show it.
- A terminal opened before the variables were saved does not have them.
- The Email Routing MX and TXT records on the bare domain are never edited.
- Domain rules from the owner's Cloudflare reference: no analytics or
  monetisation without asking, non-commercial only, no implied Cloudflare
  affiliation.
- Cloudflare calls Pages its previous version. If it is retired, only the
  upload step and the token change.

## Decisions that project makes for itself

- Whether this shell fits (see above), or a new one is needed.
- Subdomain, project name, site title, navbar pages.
- Its own design tokens, or the shared Design System's.
- Its own licence lines and source credits.
- What may be shown at all: held-back seasons stay held back.

## Getting the files

The pieces that are neutral as written: `scripts/check_site.py`,
`scripts/deploy_site.py` (three constants to change: `SITE_URL`,
`PAGES_PROJECT`, `PAGES_BRANCH`), `tests/test_deploy_site.py`,
`site/_rights.html`, `site/robots.txt` (one sitemap line to change),
`src/theme.py` with `theme/tokens.json`, and the `deploy-site` skill.
Copying them needs the owner's yes in the prediction session, as with
anything read from this repository.
