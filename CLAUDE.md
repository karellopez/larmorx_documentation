# larmorx_documentation: project context

Read this first. This repository is the documentation website of LARMORX
(`github.com/karellopez/larmorx`), published with GitHub Pages at
`https://karellopez.github.io/larmorx_documentation/`. The main repository's `CLAUDE.md` holds the
project's rules and decisions; its "Agent working rules" apply here too, as far as they concern
git, commits, usage limits and long runs.

## What lives where
- **Here:** the site: its builder (`tools/build.py`), design (`static/css/site.css`), templates,
  pages (`content/`; one per tool in `content/tools/`), data tables (`data/`), the home page hero
  (`static/js/hero.js`, `tools/hero/make_hero.py`), the Greek font subsets
  (`tools/fonts/make_greek.py`), and the rendered figures (`static/figures/<tool>/`, each with its
  provenance JSON).
- **In the main repository:** the numbers (validation records, `docs/validation/`), the benchmark
  reports, and the **code that draws the figures** (`larmorx_validation`), so that every figure can
  be regenerated from a commit of larmorx. A page here quotes numbers only from those records and
  links to them; it never computes or invents its own. The figures are drawn with
  `python -m larmorx_validation figures <tool>|all --out <this repo>/static/figures` (the main
  repository's `docs/figures.md`).

## Content rules
- **Accurate and sober.** Keep implemented and planned apart, exactly as the main repository's
  README and records do. No claims of compatibility, equivalence, platform support or clean-room
  provenance beyond what a record documents. Scientific, concise, professional; no marketing
  language.
- **Naming:** "LARMORX" in prose (Library of Algorithmic Reimplementations for MRI through Open Rust
  eXecution); `larmorx` and `larmorprepx` in code and commands. The tagline: "LARMORX — Bringing
  Neuroimaging Tools into Resonance. Reimplemented in Rust. Accessible through Python. Built for
  FAIR research."
- **Status tables** come from `data/status.yml`; update it when a tool's record changes (the
  orchestrator does this at each merge in the main repository).

## Design language (in the style of the lab's `bids_manager_documentation`)
- Printed matter: warm paper in both themes, one fixed grain layer; light and dark themes that
  follow the system, with a switch; an effects switch, off under `prefers-reduced-motion`.
- One pastel palette, the same in both themes: one pastel per software ecosystem (ANTs, AFNI, FSL,
  FreeSurfer, Workbench) and LARMORX's apricot accent; deeper variants (3:1 against the paper) for
  marks on light paper. Text is always ink.
- Instrument Serif for titles and numerals, Inter for reading, JetBrains Mono for kickers, labels
  and names. Hairline separators with a short pastel mark. Nothing is ornament for its own sake.
- Accessible: contrast, keyboard navigation, focus outlines, a still image wherever there is
  motion (no JavaScript, no WebGL2, reduced motion, effects off).
- The code is our own: `bids_manager_documentation` has no licence file, so its design language
  is followed, its code is not copied.

## Figures (CLAUDE.md rule 7 of the main repository)
- Every tool gets figures showing how the replica and the clean-room original compare with the
  original program: agreement overviews, difference distributions, image comparisons
  (registration overlays, difference maps, N4 bias fields, time series), the original's own
  variability (threads, versions), speed. Adapted to each program; elegant and consistent: one
  style sheet, a colour-blind-safe palette that matches the site's, the site's fonts.
- SVG in a light and a dark version, each at the text column's width (720 px) and a phone's (360 px); text drawn as the fonts' outlines; brain images embedded in the SVG as lossless WebP. The page shows the version of the current theme and the narrow one below 560 px: `{{ figure('<tool>/<name>', caption) }}` in a page (`tools/build.py`).
- Each figure records its provenance next to it: the validation record and larmorx commit it was
  drawn from, the data, the command.
- Keep the repository lean: no raw image data; figure files sized for the web.
- Data shown must be shareable: OpenNeuro datasets whose licence is a public-domain dedication
  (CC0-1.0, PDDL-1.0) or CC-BY (credited), templates with their notices (the MNI ICBM152 notice
  is in `static/hero/LICENSE-MNI.txt` and the footer). Brain slices only, masked, never a face.

## Build, preview, deploy
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python tools/build.py --serve     # http://localhost:8765/larmorx_documentation/
.venv/bin/python tools/build.py             # build into _site/ and check (links, anchors, headings)
.venv/bin/python tools/build.py --preview   # also _preview/index.html, one self-contained file
```
The build stops on any broken link or anchor, including links into the main repository when it is
checked out next to this one. `.github/workflows/pages.yml` builds and deploys on every push to
`main` (Pages must be enabled with Source: GitHub Actions). `tools/review/shoot.mjs` takes review
screenshots in headless Chrome (desktop and phone, light and dark).

## Licences
Fonts under the SIL Open Font License 1.1, with their licence texts in `static/fonts/`. The MNI
template's copyright notice wherever the brain is shown. The site's own code and text: Apache-2.0,
as LARMORX.

## Git
The configured identity (the user's GitHub no-reply address); never `Co-Authored-By`, "Generated
with" or any AI attribution. Agents commit and do not push; the orchestrator pushes. `.claude/`,
`_site/`, `_preview/` and `.venv/` are ignored.
