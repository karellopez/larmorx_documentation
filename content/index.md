---
title: LARMORX
template: home
description: >-
  LARMORX, the Library of Algorithmic Reimplementations for MRI through Open
  Rust eXecution: established neuroimaging tools from ANTs, AFNI, FSL and
  others, reimplemented in Rust, accessible through Python, built for FAIR
  research.
hero_kicker: Documentation · early development
hero_acronym: "*L*ibrary of *A*lgorithmic *R*eimplementations for *M*RI through *O*pen *R*ust e*X*ecution"
hero_tagline: Bringing Neuroimaging Tools into *Resonance*.
hero_lede: Reimplemented in Rust. Accessible through Python. Built for FAIR research.
hero_meta: Apache-2.0 · Linux, macOS and Windows · not yet on PyPI
hero_end_title: Many toolkits, *one* framework.
hero_end_text: Spins of five software ecosystems, precessing at one Larmor frequency, gather into one brain. Each keeps its colour.
hero_description: >-
  The animation behind this text shows spins in five groups, one for each
  software ecosystem (ANTs, AFNI, FSL, FreeSurfer and Connectome Workbench),
  each group precessing about a vertical magnetic field, B0, at its own
  frequency and out of phase. Scrolling brings their frequencies to one Larmor
  frequency and locks their phases: the spins come into resonance and gather
  into a brain, a cloud of points from the MNI ICBM 152 template, in which each
  ecosystem keeps its colour. A readout shows the coherence of the spins
  rising from about 0 to 1.
---

<section class="home-section home-intro" aria-label="LARMORX in a sentence">
<p class="lead">LARMORX is an open-source, cross-platform neuroimaging toolbox that reimplements established neuroimaging algorithms and command-line tools in Rust. <span>It aims to reproduce the functionality and behaviour of tools from ANTs, AFNI, FreeSurfer and others, without requiring you to install the original binaries or manage complex system dependencies.</span></p>
</section>

<section class="home-section" aria-labelledby="what-it-is">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">01</div>
<div>
<p class="kicker">What LARMORX is</p>
<h2 id="what-it-is">Established tools, reimplemented in <em>Rust</em></h2>
<p class="section-lede">Each tool is reimplemented in one of three ways, chosen by the licence of the original. Where a licence requires it, algorithms are reimplemented under clean-room development practices, so that restrictively licensed source code is not incorporated.</p>
</div>
<p class="margin-note"><b>Status</b>Early development. The tools listed under <a href="#status">Status</a> are implemented and validated against the original programs; everything else is planned. Not yet on PyPI: <a href="{{ repo('README.md') }}#development">build it from source</a>.</p>
</div>
<div class="ways">
<div><span class="roman">i.</span><h3>Ported from the source</h3><p>Tools with permissive licences, ANTs and ITK (Apache-2.0), are ported from their source, with each Rust function's origin recorded in the crate's <code>PROVENANCE.md</code>.</p><p class="where">larmorx · Apache-2.0</p></div>
<div><span class="roman">ii.</span><h3>A clean-room original</h3><p>Where the licence is restrictive (AFNI's GPL code, FSL), an original is written from a behavioural specification, documentation and runs of the original program, never from its source.</p><p class="where">larmorx · Apache-2.0</p></div>
<div><span class="roman">iii.</span><h3>An exact replica, kept apart</h3><p>An exact replica, where one exists, is a separate package under the upstream's licence, such as <code>larmorx-gpl</code>, that runs as a separate program. Tools with both take <code>implementation="auto" | "replica" | "original"</code>.</p><p class="where">larmorx-gpl · GPL-3.0-or-later</p></div>
</div>
<ul class="ecos" aria-label="The ecosystems and their colours">
<li class="eco-ants"><h3>ANTs and ITK</h3><p>Ported from the source: transforms, N4, denoising, ImageMath, registration (linear and deformable stages).</p><span class="state">In LARMORX</span></li>
<li class="eco-afni"><h3>AFNI</h3><p>3dTshift as a clean-room original, with an exact replica in <code>larmorx-gpl</code>.</p><span class="state">In LARMORX</span></li>
<li class="eco-fsl"><h3>FSL</h3><p>Head-motion correction with mcflirt-style options, a clean-room original, experimental.</p><span class="state">In LARMORX</span></li>
<li class="eco-freesurfer"><h3>FreeSurfer</h3><p>Planned, as its own package, <code>larmorx-freesurfer</code>.</p><span class="state state--planned">Planned</span></li>
<li class="eco-workbench"><h3>Workbench</h3><p>Connectome Workbench- and MSM-compatible surface tools.</p><span class="state state--planned">Planned</span></li>
<li class="eco-larmorx"><h3>LARMORX</h3><p>Its own NIfTI I/O and a port of fMRIPrep's one-shot BOLD resampler; the larmorprepx pipeline is planned.</p><span class="state">The accent</span></li>
</ul>
</section>

<section class="home-section" aria-labelledby="features">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">02</div>
<div>
<p class="kicker">Core features</p>
<h2 id="features">The original's arguments, the same bits on <em>every</em> platform</h2>
<p class="section-lede">Every tool can be used three ways: from Rust, from Python and from a command line that accepts the original program's arguments, with a validation record that compares it with the original, case by case.</p>
</div>
</div>
<div class="features">
<div class="feature"><span class="label">Rust</span><h3>Rust implementations</h3><p>Pure Rust, with no C, C++ or Fortran library dependencies. By design, results do not depend on the thread count, and transcendental functions come from correctly rounded <a class="body-link" href="https://core-math.gitlabpages.inria.fr/">CORE-MATH</a> ports (or the deterministic pure-Rust <code>libm</code> where not yet ported), so a tool gives the same bits on every platform.</p></div>
<div class="feature"><span class="label">Command line</span><h3>The original's arguments</h3><p><code>larmorx &lt;family&gt; &lt;program&gt; &lt;the original's arguments&gt;</code>, short alias <code>lx</code>, accepting the original's options. How far messages and exit statuses match is stated in each tool's validation record.</p></div>
<div class="feature"><span class="label">Python</span><h3>Python bindings</h3><p><code>import larmorx as lx</code>: the same tools with typed options, on in-memory images.</p></div>
<div class="feature"><span class="label">Platforms</span><h3>Six platforms, one output</h3><p>Continuous integration builds the wheels and runs the test suites on Linux (x86-64, aarch64), macOS (Intel, Apple silicon) and Windows (x64, arm64); golden tests check that every tool reproduces its Linux x86-64 output bit for bit on each platform.</p></div>
<div class="feature"><span class="label">Licences</span><h3>Two ways, kept apart</h3><p>Ported from the source where the licence is permissive; a clean-room original where it is restrictive, with exact replicas in separate packages under the upstream's licence (<a class="body-link" href="{{ repo('docs/licensing.md') }}">licensing</a>).</p></div>
<div class="feature"><span class="label">Validation</span><h3>Documented differences</h3><p>Every tool has a validation record. Defects found in the originals are recorded and corrected by default with a warning; <code>upstream_defects="reproduce"</code> gives the original's behaviour, and the parity tests run in that mode.</p></div>
</div>
<div class="try">
<div>

```bash
# the command line, with the original programs' arguments
larmorx ants N4BiasFieldCorrection -d 3 -i t1w.nii.gz -o t1w_n4.nii.gz
larmorx ants antsApplyTransforms -d 3 -i boldref.nii.gz -r t1w.nii.gz -t xfm.h5 -o boldref_t1w.nii.gz
larmorx afni 3dTshift -tpattern alt+z -TR 2 -prefix bold_stc.nii.gz bold.nii.gz
```

</div>
<div>

```python
import larmorx as lx

t1w = lx.load("t1w.nii.gz")
t1w_n4 = lx.ants.n4_bias_field_correction(t1w, n_threads=8)
boldref_t1w = lx.ants.apply_transforms(lx.load("boldref.nii.gz"), t1w, ["xfm.h5"])
bold_stc = lx.afni.tshift(lx.load("bold.nii.gz"), slice_times="alt+z", tr=2.0)
lx.save(t1w_n4, "t1w_n4.nii.gz")
```

</div>
</div>
</section>

<section class="home-section" aria-labelledby="philosophy">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">03</div>
<div>
<p class="kicker">Philosophy</p>
<h2 id="philosophy">Named after the <em>Larmor</em> frequency</h2>
<p class="section-lede">In magnetic resonance, spins of one species share one frequency. LARMORX would like the same for neuroimaging tools: many ecosystems, one shared objective.</p>
</div>
</div>
<div class="larmor">
<figure class="equation">
<span class="math" aria-label="omega equals gamma times B zero">ω = γ B<sub>0</sub></span>
<figcaption>the Larmor frequency: γ the gyromagnetic ratio, B<sub>0</sub> the field</figcaption>
</figure>
<div class="larmor-text">
<p>The name is inspired by the <strong>Larmor frequency</strong>, a fundamental concept in magnetic resonance imaging: in a uniform magnetic field B<sub>0</sub>, nuclear spins of the same species precess at the same frequency, ω = γB<sub>0</sub>.</p>
<p>In the same way, LARMORX aims to bring neuroimaging tools developed in different software ecosystems into a common computational framework, aligned toward a shared objective: <strong>FAIR</strong> scientific research, research that is Findable, Accessible, Interoperable and Reusable.</p>
</div>
</div>
<ul class="fair" aria-label="FAIR, for research software">
<li><span class="letter" aria-hidden="true">F</span><h3>Findable</h3><p>A public repository with versioned history; PyPI releases with citation metadata are planned.</p></li>
<li><span class="letter" aria-hidden="true">A</span><h3>Accessible</h3><p>Open source under Apache-2.0; native builds with no external neuroimaging installations, containers or administrator rights.</p></li>
<li><span class="letter" aria-hidden="true">I</span><h3>Interoperable</h3><p>Standard formats (NIfTI-1/2, ITK transform files including HDF5), the original tools' command-line arguments, and a Python API for pipelines.</p></li>
<li><span class="letter" aria-hidden="true">R</span><h3>Reusable</h3><p>A permissive licence, per-tool documentation, provenance records, case-by-case validation records and a register of the differences from the originals.</p></li>
</ul>
<p class="fair-source">The project follows the FAIR Principles for Research Software, <a class="body-link" href="https://doi.org/10.15497/RDA00068">FAIR4RS</a>.</p>
</section>

<section class="home-section" aria-labelledby="status">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">04</div>
<div>
<p class="kicker">Current status</p>
<h2 id="status">What is implemented, and what is <em>planned</em></h2>
<p class="section-lede">Implemented and validated against the original programs (ANTs 2.6.5, AFNI 25.2.09, FSL 6.0.7, nibabel). Each tool's name leads to its page, with figures comparing it with the original; each line links to its validation record in the main repository. Everything else is planned.</p>
</div>
<p class="margin-note"><b>In the repository</b>API pages are in <a href="{{ repo('docs/api/') }}">docs/api</a>, benchmark reports in <a href="{{ repo('docs/benchmarks/') }}">docs/benchmarks</a>, and the defects found in the originals in the <a href="{{ repo('docs/findings/upstream-defects.md') }}">register</a>.</p>
</div>
<div class="status-head"><h3>Implemented and validated</h3><p>{{ data.status.implemented | length }} lines · standard tier</p></div>
<div class="table-wrap">
<table class="tools">
<thead><tr><th scope="col">Tool</th><th scope="col">How</th><th scope="col">Validation</th></tr></thead>
<tbody>
{%- for row in data.status.implemented %}
<tr class="eco-{{ row.eco }}"><td><span class="tool-name"><span class="dot" title="{{ eco[row.eco].long }}"></span>{% if row.page %}<a href="{{ link(row.page) }}">{{ row.tool | md_inline }}</a>{% else %}<span>{{ row.tool | md_inline }}</span>{% endif %}</span><span class="tool-use">{% for u in row.use %}<code>{{ u }}</code>{% endfor %}</span></td><td class="how">{{ row.how | md_inline }}</td><td class="val">{{ row.validation | md_inline }}</td></tr>
{%- endfor %}
</tbody>
</table>
</div>
<div class="status-head"><h3>Planned</h3><p>in order, from the roadmap</p></div>
<ol class="plan">
{%- for item in data.status.planned %}
<li><h3><span class="dots">{% for e in item.eco %}<span class="dot eco-{{ e }}" title="{{ eco[e].long }}"></span>{% endfor %}</span>{{ item.title }}</h3><p>{{ item.text | md_inline }}</p></li>
{%- endfor %}
</ol>
<p class="status-note">LARMORX is not on PyPI yet. The planned distribution is <code>pip install larmorx</code> for the library and the <code>larmorx</code> and <code>lx</code> commands, with extras for exact replicas of GPL-licensed tools (<code>larmorx[exact]</code>) and the larmorprepx pipeline (<code>larmorx[prep]</code>). Until then, <a class="body-link" href="{{ repo('README.md') }}#development">build it from source</a>.</p>
<div class="closing">
<p>How every tool is compared with the original program, and where the records are.</p>
<a class="btn btn--secondary" href="{{ link('/validation/') }}">Validation<svg aria-hidden="true"><use href="#i-arrow-right"/></svg></a>
</div>
</section>
