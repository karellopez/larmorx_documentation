# LARMORX documentation

The documentation site of [LARMORX](https://github.com/karellopez/larmorx), the
Library of Algorithmic Reimplementations for MRI through Open Rust eXecution, to
be published at <https://karellopez.github.io/larmorx_documentation/>.

The pages are Markdown, built into a static site by a small Python program.
GitHub Actions builds and deploys it on every push to `main`
(`.github/workflows/pages.yml`); the built site, `_site/`, is not committed.

## Build and preview

Create the environment and fetch the evidence's images, from the branch `evidence-blobs` (below):

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
python3 tools/blobs.py fetch
```

Then build, serve on <http://localhost:8765/larmorx_documentation/> and rebuild on every change;
or build into `_site/` and check it; or also write `_preview/index.html`, the home page as one file:

```bash
.venv/bin/python tools/build.py --serve
.venv/bin/python tools/build.py
.venv/bin/python tools/build.py --preview
```

Every build checks what it wrote: internal links and their anchors, one `h1`
per page, heading levels that do not skip, leftovers of the template language,
comments in the shell blocks people copy, and, when the main repository is
checked out next to this one (`../larmorx`, or `--main-repo`), that every file
a page links to there exists and that every program's reference page is
current. Problems stop the build.

`--preview` writes the home page as one self-contained file (CSS and
JavaScript inline, the hero's data as a data URI, fonts from Google Fonts),
for a quick look on any device without a server.

## Layout

```
content/          the pages: Markdown with YAML front matter, rendered as Jinja first, then Markdown
content/evidence/ a program's evidence page each (content/tools/ keeps their old addresses as redirects)
content/programs/ the Programs page and the reference pages, written by the main repository's exporter
content/concepts/ Concepts and Why Rust and Python; content/validation/: the data panel
data/             the site's data: the software and their colours (ecosystems.yml), the status (from the
                  main README), the Programs page's groups (programs.yml, generated)
templates/        the layouts: base, home, doc, reference, redirect, 404
static/css/       site.css, the design system
static/js/        site.js (theme, effects, menu, copy buttons), hero.js (the home page hero, WebGL2)
static/hero/      the hero's points (hero.bin) and its stills (hero-light.svg, hero-dark.svg)
static/fonts/     Instrument Serif, Inter, JetBrains Mono, and the Greek letters of Inter, JetBrains Mono
                  and Noto Serif Display (SIL Open Font License, texts beside them)
static/evidence/  the interactive evidence, exported by the main repository
                  (larmorx_validation.evidence): <page>.json, summary.json, panel.json, difftest.json,
                  blobs.sha256 (the manifest); blobs/ is git-ignored (the branch evidence-blobs)
static/js/        also evidence.js (the viewer, charts, case explorer, number check)
static/css/       also evidence.css (the verdicts, the viewer, the evidence tables and charts)
data/verdicts.yml the verdict taxonomy: one legend for the whole site
tools/evidence.py the evidence's HTML, used by the builder
static/brand/     the mark and the icons
site.yml          the site's name, address, repositories and navigation
tools/build.py    the builder
tools/blobs.py    the evidence images' branch: fetch, verify, commit (evidence-blobs)
tools/hero/       make_hero.py, which precomputes static/hero/ from the MNI template
tools/fonts/      make_greek.py, which cuts the Greek subsets in static/fonts/ (fontTools, brotli)
tools/review/     shoot.mjs, which photographs pages in headless Chrome, for review
```

A page is `content/<name>.md` (or `content/<name>/index.md`), published at `/<name>/`. Its front matter
gives `title`, `lede`, `kicker` and `description`; `template: home` selects
the home layout. In a page, `{{ link('/validation/') }}` links within the site,
`{{ repo('docs/validation/golden.md') }}` links to a file in the main
repository, and Markdown links may be written `[text](repo:docs/...)` or
`[text](/validation/)`. A heading may set its id: `## Title {#id}`.

Each program has two pages. Its evidence page is `content/evidence/<page>.md`, published
at `/evidence/<page>/` (listed under `tools` in `site.yml` with its software, `eco`, and
linked from the status table by `page:` in `data/status.yml`); since 2026-10-21 every
evidence page is interactive (below), and `content/tools/<page>.md` keeps its old address
as a redirect. Its reference page is `content/programs/<group>/<program>.md`, written by
the main repository's exporter (`python -m larmorx_validation reference all --site <this
checkout>`), never by hand, and the Programs page's data, `data/programs.yml`, the same
way. A redirect page (`redirect: /new/address/`, with `anchors:` for sections that moved
to another page) keeps an old address working. The builder still renders a static figure
placed with `{{ figure('<tool>/<name>', 'caption') }}` (from `static/figures/<tool>/`,
drawn by the main repository's `larmorx_validation.figures`), which no page uses any more.

### The validation evidence

Every evidence page and the Validation page are interactive evidence: they set
`evidence: true` (loads `static/css/evidence.css`
and `static/js/evidence.js`) and `wide: true` (a wider column, the table of
contents in the sidebar). Their data are exported by the main repository:
`python -m larmorx_validation evidence <page>|summary|all --site <this checkout>`
writes `static/evidence/<page>.json` (the worked examples, metrics, verdicts,
cases, chart data and provenance), `static/evidence/summary.json` (the Validation
page's summary of every program) and the images in `static/evidence/blobs/`, named
by their SHA-256 so an unchanged export changes nothing. A page places them with

- `{{ ev.example('<page>', '<example>') }}`: the image viewer (still panels
  without JavaScript), the chain of causes, the metrics table, the provenance; a
  panel whose JSON has `overlay: {<output>: {on: <panel>, window: [lo, hi]}}`
  draws that output (a mask) over the other panel's image, tinted, with its edge
  in the slice (since 2026-10-23: 3dAutomask, 3dUnifize);
- `{{ ev.agreement('<page>', '<port>') }}`, `{{ ev.band('<page>') }}`,
  `{{ ev.speed('<page>') }}`, `{{ ev.dots('<page>', '<id>') }}` (dots on a log
  axis, such as a thread band): the charts, in HTML;
- `{{ ev.table('<page>', '<id>') }}`: a table of the JSON's `tables` (numbers with
  their pointers, verdicts); an example's own `tables` and `lines` (panels of lines
  over one axis, such as a run's motion parameters, redrawn by the script with the
  values under the pointer) are drawn inside it;
- `{{ ev.cases('<page>') }}`: every case of the records (search, filters, sorting,
  `#case=<id>` links with JavaScript); `{{ ev.cases('<page>', '<port>') }}`
  lists one port's (one explorer per program on a page of several, the
  agreement chart's segments filtering their own);
- `{{ ev.random_testing('<page address>', '<page>') }}` and
  `{{ ev.random_testing_summary() }}`: random testing, from
  `static/evidence/difftest.json`, on an evidence page and on the Validation page;
- `{{ ev.random_testing_runs() }}`: the table of the runs since the long run, one row per
  program, port and run, from `difftest.json`'s `runs`;
- `{{ verdict('<id>') }}`, `{{ ev.legend() }}`, `{{ ev.taxonomy() }}`,
  `{{ ev.matrix(site.tools, data.programs.groups) }}`: the verdicts of
  `data/verdicts.yml`; the matrix is every program's ports and verdicts, grouped by
  software in the Programs page's order.

- `{{ ev.panel_table() }}`, `{{ ev.panel_coverage() }}`, `{{ ev.panel_details() }}`:
  the Data panel page (`content/validation/data-panel.md`) from `static/evidence/panel.json`
  (`python -m larmorx_validation evidence panel`): the datasets, the criteria each
  covers, each dataset's credit line and defacing check.

Every example carries the credit line of the data it shows, and every evidence page
ends with **Data credits** (every dataset its examples, cases and tables name), both
generated from LARMORX's test-data catalog (the JSON's `credits`): for CC BY data a
proper attribution with the changes made, for CC BY-SA data the share-alike notice.
A new data-panel case may be exported as a **slices view** (the JSON's `view`: three
full-resolution slices through one voxel, cropped only where every array is exactly
constant, the constant drawn as it is); it says so under its panels, and its viewer keeps
the slice fixed per plane. Existing examples stay whole volumes.

**The images live on the orphan branch `evidence-blobs`, not on `main`.**
`static/evidence/blobs/` is git-ignored; `static/evidence/blobs.sha256` (written by the
export: every blob a JSON names, with its full SHA-256) is committed with the JSON and
pins them. `tools/blobs.py`:

- `python3 tools/blobs.py fetch`: fetch `evidence-blobs` from origin, extract it into
  `static/evidence/blobs/` and verify it;
- `python3 tools/blobs.py verify`: every blob of the manifest is there, its hash right,
  every JSON's blob listed;
- `python3 tools/blobs.py commit`: after an export, the branch `evidence-blobs` as one
  parentless commit of the manifest's blobs (the same blobs give the same commit).

Publish the images first, then the JSON and the manifest:

```bash
git push --force origin evidence-blobs
git push origin main
```

The Pages workflow checks `evidence-blobs` out into `_blobs/`, verifies it against the
manifest (`tools/blobs.py publish-dir`: a missing, extra or altered blob stops the
deployment) and publishes the blobs with the site. The branch is replaced at every export,
so the images of a superseded export leave the repository; `main`'s history grows by the
JSON only. Every export also checks the published size (`python -m larmorx_validation
evidence sizes`): at most 500 MB in all, and 40 MB per page unless a page's budget is raised with its reason (N4's: 60 MB); the guard never removes content.

`tools/evidence.py` renders them; the build refuses an unknown verdict or a
missing blob. Every number a page shows carries its JSON pointer (`data-ev`);
the review check compares them with the JSON, and the viewers' decoded images
with the values the JSON records at each largest difference:

```bash
node tools/review/shoot.mjs --url http://localhost:8765/larmorx_documentation/evidence/ants-n4/ \
     --out shots --name check --sizes 1440x900 --themes light \
     --eval "LX_EVIDENCE.check().then(r => [r.checked, r.agree, r.disagree])"
node tools/review/shoot.mjs --url http://localhost:8765/larmorx_documentation/evidence/ants-n4/ \
     --out shots --name check --sizes 1440x900 --themes light \
     --eval "(async () => { for (const e of document.querySelectorAll('.ev-example')) { e.scrollIntoView(); await new Promise(r => setTimeout(r, 2500)); } return (await LX_EVIDENCE.checkViewers()).filter(x => !x.ok); })()"
```

## The design

Printed matter: warm paper in both themes (light grey by day, grey-black by
night) under one fixed grain layer; one pastel palette, the same in both
themes, with one pastel for each of eight projects LARMORX ports from or plans
to (ANTs, AFNI, FSL, FreeSurfer, Connectome Workbench, tedana, sdcflows,
fMRIPrep; `data/ecosystems.yml`) and LARMORX's apricot as the accent, deeper
variants of the same hues for marks on light paper; text always ink. A
software's pastel appears only with its name (a chip, a group's band); the
original, the replica and the clean room have colours, lines and marks of their
own (ink, blue, apricot: the main repository's `docs/writing-guide.md`, section 5). Instrument Serif for
titles and numerals, Inter for reading, JetBrains Mono for kickers and labels.
Hairline separators with a short pastel mark. The theme follows the system
unless the reader chooses; the effects switch stops every animation and is
off by default when the system asks for reduced motion.

## The hero

The home page hero is spins coming into resonance. Each point is a spin of
one of five projects (ANTs, AFNI, FSL, FreeSurfer, Connectome Workbench), in its pastel. At the top of the page the spins sit in five
ensembles, rings precessing about a vertical field B₀, each at its own
frequency and with random phases: dephased, with a coherence near 0. As the
reader scrolls, the frequencies converge on one Larmor frequency and the
phases lock (coherence 1), and the spins gather into a brain sampled from the
MNI ICBM 152 2009c template, turning slowly about B₀, each project keeping
its colour. A readout shows the coherence, |⟨e^{iφ}⟩|, and the frequency
spread.

`static/hero/` is precomputed and committed. To make it again (numpy, scipy
and nibabel; TemplateFlow's `tpl-MNI152NLin2009cAsym`):

```bash
python tools/hero/make_hero.py --templateflow <TemplateFlow home>
```

Without WebGL2, with the effects off or without JavaScript, the hero shows
the still drawings. A slow machine steps down: first the resolution, then the
number of spins.

## Reviewing

```bash
node tools/review/shoot.mjs --url http://localhost:8765/larmorx_documentation/ --out shots \
     --sizes 1440x900,390x844 --themes light,dark --at hero:0,0.5,1 --at y:2400
```

Needs Node 22 and Google Chrome; WebGL2 runs on SwiftShader there.

## Credits

The hero's points are sampled from the MNI ICBM 152 nonlinear asymmetric
template, version 2009c (Fonov et al., NeuroImage 2011; 2009), as distributed
by TemplateFlow; Copyright (C) 1993–2004 Louis Collins, McConnell Brain
Imaging Centre, Montreal Neurological Institute, McGill University, under the
notice in `static/hero/LICENSE-MNI.txt`. The fonts are under the SIL Open
Font License 1.1 (`static/fonts/*-OFL.txt`).
