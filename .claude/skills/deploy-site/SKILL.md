---
name: deploy-site
description: Check the site and publish it to hydrowhiplash.dacekroberts.dev (Cloudflare Pages, direct upload). Use before every publication, first or rolling, and whenever the owner asks whether the site is ready to go live. Runs the readiness checks, stages a build, and uploads only on the owner's yes for that upload.
---

# Check and publish the site

One procedure for every publication (ACTION_PLAN "Rolling publication",
D76; hosting, D84). The upload publishes to a public address, so it is
asked for every time: an earlier yes does not carry over.

## Steps

1. **Commit and push first.** `scripts/deploy_site.py` refuses an
   uncommitted or unpushed checkout, so a published site always matches
   one pushed commit. `handoff_cloudflare-setup_reference.md` is ignored
   by git on purpose; read it before anything touches the domain.
2. **Readiness of each piece (the rule in ACTION_PLAN):**
   - the licence of every source behind a page has a verdict in
     `DATA_SOURCES.md` (`read-licence` skill for a new source);
   - anything that sets burned area beside ENSO: the registered runs are
     committed (tag `registered-run1`);
   - every required credit is on `site/methods.qmd` ("Data sources and
     attribution"): compare its table and notices with the ledger's
     "Required notices". A source added for display still needs its row.
3. **Rights and outside requests:**
   - the footer's copyright line is on every page and the rights tags of
     `site/_rights.html` are in every page's head;
   - `robots.txt` in the build is the project's own (`site/robots.txt`:
     AI-training crawlers asked to stay out, search engines allowed);
   - the built site asks no other host for anything: fonts and plotly.js
     are served from the site. Check a page's network requests in the
     browser, or search the built HTML for `src="http`.
4. **Domain rules** (the owner's Cloudflare reference): no analytics, no
   monetisation, no implied Cloudflare affiliation, a credit wherever a map
   appears, and the Email Routing MX and TXT records on the bare domain are
   never edited.
5. **Stage and read the report:**
   `python scripts/deploy_site.py` (inside the `whiplash` env). It renders
   the site, checks every page and link, refuses the word "draft" in any
   page's visible text ("work in progress" is allowed: owner, 2026-10-12),
   checks the host's size limits, and writes `dist/site/` with
   `dist/deploy_manifest.json`. Report to the owner: the commit, the file
   count and size, and any page it named.
6. **Look at it.** Open the pages in the browser preview (`.claude/launch.json`,
   "site") in light and dark and at phone width when anything visible
   changed since the last publication.
7. **Ask the owner, then upload:** `python scripts/deploy_site.py --upload`.
   It needs `wrangler` on the PATH and `CLOUDFLARE_API_TOKEN` and
   `CLOUDFLARE_ACCOUNT_ID` in the environment (set by the owner; never
   printed, never asked for in a chat). If the session cannot see them, the
   app needs a restart, not a new token.
8. **Check the live address.** Load each page at
   https://hydrowhiplash.dacekroberts.dev and confirm the footer, one
   chart and the map draw. `.dev` is HTTPS only. In the browser, list the
   hosts the page asked: none besides the site. `curl` and `fetch` are
   not a valid check for this (see the traps).
9. **Record it.** A line in the day's log with the commit and the time,
   and a `DECISIONS.md` entry for the first publication of any new piece.

## Traps met so far

- wrangler 4 hands `pages project create` to the Workers-based hosting
  unless `--force` is given; the project `hydrowhiplash` was created that
  way once (2026-10-12) and later commands do not need the flag.
- The token is limited to "Pages: Edit". It cannot add the custom domain
  or touch DNS: the owner does that in the dashboard.
- Cloudflare labels Pages its previous version. If it is retired, only the
  upload step of `scripts/deploy_site.py` and the token change.
- The preview server stops when the desktop app restarts; start it again
  before step 6.
- Cloudflare adds an analytics script (`static.cloudflareinsights.com`)
  to every page of a proxied domain by default on the Free plan: "Real
  User Measurements (RUM)". Found on the custom domain the day it went
  live (2026-10-12); the build and the pages.dev address had none. The
  owner switched it off for dacekroberts.dev (Domains, the domain, Speed,
  Real User Measurements, "Disable completely"). It is added only to
  document loads, so only a real browser shows it. A new domain starts
  with it on.
- A terminal opened before the token variables were saved does not have
  them; the upload then stops with "Nothing was sent".
