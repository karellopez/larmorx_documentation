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
  (`tools/fonts/make_greek.py`), and the validation evidence (`static/evidence/`, exported by the
  main repository).
- **In the main repository:** the numbers (validation records, `docs/validation/`), the benchmark
  reports, and the **code that computes the evidence** (`larmorx_validation.evidence`), so that
  every number and image can be regenerated from a commit of larmorx. A page here quotes numbers
  only from those records and the exported evidence and links to them; it never computes or
  invents its own. The evidence is exported with
  `python -m larmorx_validation evidence <tool>|summary|all --site <this repo>` (the main
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

## Validation evidence (CLAUDE.md rule 7 of the main repository)
- Since 2026-10-21 (the user found the static figures unclear and short of evidence) every tool's
  page shows **interactive evidence**: worked examples on real data with the raw input, the
  original program's outputs (each panel naming its version, build, threads and maths), larmorx's
  outputs (port, replica, clean-room original; default and `reproduce` modes), difference panels
  beside the original's own variability on the same scale, a metrics table with a **verdict and
  its reason** for every comparison, and the record's cases in a case explorer. How it works and
  how to add a tool: README.md, "The validation evidence"; the export: the main repository's
  `docs/figures.md` (`python -m larmorx_validation evidence <tool>|summary|all --site <this repo>`).
- One verdict taxonomy for the whole site (`data/verdicts.yml`, defined on the Validation page);
  colour plus pattern plus name, never colour alone.
- The data under `static/evidence/` is content-addressed and byte-deterministic (a re-export of
  unchanged results changes nothing in git); brain-masked or cropped, never a face; only data
  whose licence allows it (OpenNeuro CC0-1.0 or PDDL-1.0, or CC-BY credited; templates with their
  notices, the MNI notice in `static/hero/LICENSE-MNI.txt` and the footer).
- Every number shown comes from the records or from metrics computed offline; check them with
  `tools/review/shoot.mjs --eval` before publishing. Review every component state (desktop and
  phone, light and dark) for meaning as well as looks; a pilot goes to the user before a design is
  rolled out.
- Every tool's page is evidence since part 2b (2026-10-21); the static figures of part 1
  (`static/figures/`) were removed (`larmorx_validation.figures` can still draw them).

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
