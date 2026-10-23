# LARMORX documentation

The documentation site of [LARMORX](https://github.com/karellopez/larmorx), the
Library of Algorithmic Reimplementations for MRI through Open Rust eXecution, to
be published at <https://karellopez.github.io/larmorx_documentation/>.

The pages are Markdown, built into a static site by a small Python program.
GitHub Actions builds and deploys it on every push to `main`
(`.github/workflows/pages.yml`); the built site, `_site/`, is not committed.

## Build and preview

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python tools/build.py --serve      # build, serve on http://localhost:8765/larmorx_documentation/, rebuild on change
.venv/bin/python tools/build.py              # build into _site/ and check it
.venv/bin/python tools/build.py --preview    # also write _preview/index.html: the home page as one file
```

Every build checks what it wrote: internal links and their anchors, one `h1`
per page, heading levels that do not skip, leftovers of the template language,
and, when the main repository is checked out next to this one (`../larmorx`,
or `--main-repo`), that every file a page links to there exists. Problems stop
the build.

`--preview` writes the home page as one self-contained file (CSS and
JavaScript inline, the hero's data as a data URI, fonts from Google Fonts),
for a quick look on any device without a server.

## Layout

```
content/          the pages: Markdown with YAML front matter, rendered as Jinja first, then Markdown
data/             the site's data: the ecosystems and their colours, the status (from the main README)
templates/        the layouts: base, home, doc, 404
static/css/       site.css, the design system
static/js/        site.js (theme, effects, menu, copy buttons), hero.js (the home page hero, WebGL2)
static/hero/      the hero's points (hero.bin) and its stills (hero-light.svg, hero-dark.svg)
static/fonts/     Instrument Serif, Inter, JetBrains Mono, and the Greek letters of Inter, JetBrains Mono
                  and Noto Serif Display (SIL Open Font License, texts beside them)
static/evidence/  the interactive evidence, exported by the main repository
                  (larmorx_validation.evidence): <tool>.json, summary.json, blobs/
static/js/        also evidence.js (the viewer, charts, case explorer, number check)
static/css/       also evidence.css (the verdicts, the viewer, the evidence tables and charts)
data/verdicts.yml the verdict taxonomy: one legend for the whole site
tools/evidence.py the evidence's HTML, used by the builder
static/brand/     the mark and the icons
site.yml          the site's name, address, repositories and navigation
tools/build.py    the builder
tools/hero/       make_hero.py, which precomputes static/hero/ from the MNI template
tools/fonts/      make_greek.py, which cuts the Greek subsets in static/fonts/ (fontTools, brotli)
tools/review/     shoot.mjs, which photographs pages in headless Chrome, for review
```

A page is `content/<name>.md`, published at `/<name>/`. Its front matter
gives `title`, `lede`, `kicker` and `description`; `template: home` selects
the home layout. In a page, `{{ link('/validation/') }}` links within the site,
`{{ repo('docs/validation/golden.md') }}` links to a file in the main
repository, and Markdown links may be written `[text](repo:docs/...)` or
`[text](/validation/)`. A heading may set its id: `## Title {#id}`.

A tool's page is `content/tools/<tool>.md` (listed under `tools` in `site.yml`,
linked from the status table by `page:` in `data/status.yml`); since 2026-10-21 every
tool's page is interactive evidence (below). The builder still renders a static
figure placed with `{{ figure('<tool>/<name>', 'caption') }}` (from
`static/figures/<tool>/`, drawn by the main repository's `larmorx_validation.figures`),
which no page uses any more.

### The validation evidence

Every tool's page and the Validation guide are interactive evidence: they set
`evidence: true` (loads `static/css/evidence.css`
and `static/js/evidence.js`) and `wide: true` (a wider column, the table of
contents in the sidebar). Their data are exported by the main repository:
`python -m larmorx_validation evidence <tool>|summary|all --site <this checkout>`
writes `static/evidence/<tool>.json` (the worked examples, metrics, verdicts,
cases, chart data and provenance), `static/evidence/summary.json` (the Validation
page's summary of every tool) and the images in `static/evidence/blobs/`, named
by their SHA-256 so an unchanged export changes nothing. A page places them with

- `{{ ev.example('<tool>', '<example>') }}`: the image viewer (still panels
  without JavaScript), the chain of causes, the metrics table, the provenance; a
  panel whose JSON has `overlay: {<output>: {on: <panel>, window: [lo, hi]}}`
  draws that output (a mask) over the other panel's image, tinted, with its edge
  in the slice (since 2026-10-23: 3dAutomask, 3dUnifize);
- `{{ ev.agreement('<tool>', '<implementation>') }}`, `{{ ev.band('<tool>') }}`,
  `{{ ev.speed('<tool>') }}`, `{{ ev.dots('<tool>', '<id>') }}` (dots on a log
  axis, such as a thread band): the charts, in HTML;
- `{{ ev.table('<tool>', '<id>') }}`: a table of the JSON's `tables` (numbers with
  their pointers, verdicts); an example's own `tables` and `lines` (panels of lines
  over one axis, such as a run's motion parameters, redrawn by the script with the
  values under the pointer) are drawn inside it;
- `{{ ev.cases('<tool>') }}`: every parity case (search, filters, sorting,
  `#case=<id>` links with JavaScript); `{{ ev.cases('<tool>', '<implementation>') }}`
  lists one implementation's (one explorer per program on a page of several, the
  agreement chart's segments filtering their own);
- `{{ verdict('<id>') }}`, `{{ ev.legend() }}`, `{{ ev.taxonomy() }}`,
  `{{ ev.matrix(site.tools) }}`: the verdicts of `data/verdicts.yml`.

`tools/evidence.py` renders them; the build refuses an unknown verdict or a
missing blob. Every number a page shows carries its JSON pointer (`data-ev`);
the review check compares them with the JSON, and the viewers' decoded images
with the values the JSON records at each largest difference:

```bash
node tools/review/shoot.mjs --url http://localhost:8765/larmorx_documentation/tools/ants-n4/ \
     --out shots --name check --sizes 1440x900 --themes light \
     --eval "LX_EVIDENCE.check().then(r => [r.checked, r.agree, r.disagree])"
node tools/review/shoot.mjs --url http://localhost:8765/larmorx_documentation/tools/ants-n4/ \
     --out shots --name check --sizes 1440x900 --themes light \
     --eval "(async () => { for (const e of document.querySelectorAll('.ev-example')) { e.scrollIntoView(); await new Promise(r => setTimeout(r, 2500)); } return (await LX_EVIDENCE.checkViewers()).filter(x => !x.ok); })()"
```

## The design

Printed matter: warm paper in both themes (light grey by day, grey-black by
night) under one fixed grain layer; one pastel palette, the same in both
themes, with one pastel per software ecosystem (ANTs, AFNI, FSL, FreeSurfer,
Connectome Workbench) and LARMORX's apricot as the accent, deeper variants of
the same hues for marks on light paper; text always ink. Instrument Serif for
titles and numerals, Inter for reading, JetBrains Mono for kickers and labels.
Hairline separators with a short pastel mark. The theme follows the system
unless the reader chooses; the effects switch stops every animation and is
off by default when the system asks for reduced motion.

## The hero

The home page hero is spins coming into resonance. Each point is a spin of
one ecosystem, in its pastel. At the top of the page the spins sit in five
ensembles, rings precessing about a vertical field B₀, each at its own
frequency and with random phases: dephased, with a coherence near 0. As the
reader scrolls, the frequencies converge on one Larmor frequency and the
phases lock (coherence 1), and the spins gather into a brain sampled from the
MNI ICBM 152 2009c template, turning slowly about B₀, each ecosystem keeping
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
