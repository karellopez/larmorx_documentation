---
title: LARMORX
template: home
description: >-
  LARMORX, the Library of Algorithmic Reimplementations for MRI through Open
  Rust eXecution: programs from ANTs, AFNI, FSL, tedana, sdcflows and fMRIPrep,
  reimplemented and compared with their originals, in one Python package, built
  for FAIR research.
hero_kicker: Documentation · early development
hero_acronym: "*L*ibrary of *A*lgorithmic *R*eimplementations for *M*RI through *O*pen *R*ust e*X*ecution"
hero_tagline: Bringing Neuroimaging Tools into *Resonance*.
hero_lede: Reimplemented in Rust. Accessible through Python. Built for FAIR research.
hero_meta: Apache-2.0 · Linux, macOS and Windows · pip install larmorx
hero_end_title: Many neuroimaging toolboxes working synergistically in *one* package.
hero_end_text: Five groups of spins, one colour each for ANTs, AFNI, FSL, FreeSurfer and Workbench, come to one frequency and gather into a brain from the MNI template.
hero_description: >-
  The animation behind this text shows spins in five groups, one for each of
  five software projects (ANTs, AFNI, FSL, FreeSurfer and Connectome
  Workbench), each group precessing about a vertical magnetic field, B0, at its
  own frequency and out of phase. Scrolling brings their frequencies to one
  Larmor frequency and locks their phases: the spins come into resonance and
  gather into a brain, a cloud of points from the MNI ICBM 152 template, in
  which each group keeps its colour. A readout shows the coherence of the spins
  rising from about 0 to 1.
---

<section class="home-section home-intro" aria-label="What LARMORX gives">
<p class="lead">LARMORX puts programs from ANTs, AFNI, FSL, tedana, sdcflows and fMRIPrep in one Python package. <span><code>pip install larmorx</code> is all it takes on Linux, macOS and Windows: no other installation, and the same results on every computer.</span></p>
<p class="intro-note">Most programs are ports of an original program, reimplemented in Rust (or kept in Python, where the original is Python) and compared with it case by case. The tests check on six platforms that every program gives the same results. LARMORX is in early development: its first release, 0.1.0rc1, is a pre-release. This site describes the code in development (the repository's main branch) and marks what 0.1.0rc1 does not have yet "from the next release": tedana's <code>t2smap</code> in <code>larmorx</code> itself, for one, which 0.1.0rc1 has only in <code>larmorx-gpl</code>. The programs under <a class="body-link" href="#status">Where it stands</a> are ported and compared with their originals; everything else is planned. How to install it and run its first programs: <a class="body-link" href="{{ link('/getting-started/') }}">Getting started</a>; the words, packages and settings in depth: <a class="body-link" href="{{ link('/concepts/') }}">Concepts</a>.</p>
</section>

<section class="home-section" aria-labelledby="what-it-is">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">01</div>
<div>
<p class="kicker">Original, replica, clean room</p>
<h2 id="what-it-is">Every program is compared with its <em>original</em></h2>
<p class="section-lede">Most of LARMORX's programs are ports of original programs. Each port is a replica or a clean room, and some programs have both. The original's licence decides which package each port goes in.</p>
</div>
<p class="margin-note"><b>One example</b><code>bet</code>, which finds the brain in a head image, runs through the three cards. On fMRIPrep's own call, its replica and its clean room both give FSL's brain and mask, every voxel: <a href="{{ link('/evidence/fsl-bet/#example') }}">its evidence</a>.</p>
</div>
<div class="ways">
<div><span class="roman">i.</span><h3>Original</h3><p>The program as its own developers release it. Every port runs beside it, on the same files with the same arguments, and is compared with it: its files, its messages and its exit status.</p><p class="ex"><code>bet</code> from FSL 6.0.7.23.</p><p class="where">ANTs 2.6.5 · AFNI 26.3.05 · FSL 6.0.7.23<br>tedana 26.0.3 · sdcflows 2.17.1 · fMRIPrep's steps</p></div>
<div><span class="roman">ii.</span><h3>Replica</h3><p>The original's source translated step by step into Rust, or, for some Python originals, rewritten step by step in Python, to give its results bit for bit. A replica comes under its original's licence terms: the replicas of ANTs, ITK, AFNI, sdcflows and fMRIPrep are in <code>larmorx</code>, FSL's in <code>larmorx-nc</code>, and tedana's <code>t2smap</code> in <code>larmorx-gpl</code>, under GPL-3.0. <code>larmorx-nc</code> and <code>larmorx-gpl</code> are installed apart and run as separate programs.</p><p class="ex"><code>bet</code>'s replica, in <code>larmorx-nc</code>.</p><p class="where">larmorx · Apache-2.0 (AFNI's with its CC BY 4.0 credit)<br>larmorx-nc · FSL Licence, non-commercial use only<br>larmorx-gpl · GPL-3.0</p></div>
<div><span class="roman">iii.</span><h3>Clean room</h3><p>Written again from a description of what the original does, its documentation and runs of it, never from its source, and built for speed. It carries LARMORX's licence, Apache-2.0, so it is in <code>larmorx</code>: AFNI's and FSL's programs have one, and tedana's <code>t2smap</code> from the next release.</p><p class="ex"><code>bet</code>'s clean room, in <code>larmorx</code>, written without FSL's source.</p><p class="where">larmorx · Apache-2.0</p></div>
</div>
<p class="ways-note">A program with both ports takes <code>implementation="replica"</code> or <code>"clean-room"</code> (<code>"original"</code> in 0.1.0rc1). <code>"auto"</code>, the default, runs the replica when it is installed (AFNI's are built in) and the clean room otherwise. Every program and its ports: <a class="body-link" href="{{ link('/programs/') }}">Programs</a>. The four words, the packages and their licences in full: <a class="body-link" href="{{ link('/concepts/') }}">Concepts</a> and the repository's <a class="body-link" href="{{ repo('docs/licensing.md') }}">licensing notes</a>.</p>
</section>

<section class="home-section" aria-labelledby="software">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">02</div>
<div>
<p class="kicker">Programs by their software</p>
<h2 id="software">Programs from six projects, and two <em>planned</em></h2>
<p class="section-lede">Each project has a colour, always shown with its name. The <a class="body-link" href="{{ link('/programs/') }}">Programs</a> page lists every program, what it does and which ports it has.</p>
</div>
</div>
<ul class="ecos ecos--software" aria-label="The software LARMORX ports, with its colours">
{%- for g in data.programs.groups %}
<li class="eco-{{ g.id }}"><h3>{{ g.name }}</h3>{% if g.get('planned') %}<p>{{ g.planned | md_inline }}</p><span class="state state--planned">Planned</span>{% else %}<p>{{ g.summary | md_inline }}</p>{% if g.id != 'larmorx' %}<p class="eco-ports">{% for p in g.ports %}<span class="port port--{{ p.kind }}"><span class="port-name">{{ p.name }}</span> <code>{{ p.package }}</code>{% if p.next_release %} <span class="prog-next">from the next release</span>{% endif %}</span>{% endfor %}</p>{% endif %}<a class="state" href="{{ link('/programs/#' ~ g.id) }}">{{ g.count }}</a>{% endif %}</li>
{%- endfor %}
</ul>
</section>

<section class="home-section" aria-labelledby="features">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">03</div>
<div>
<p class="kicker">How to use it</p>
<h2 id="features">The original's arguments, the same bits on <em>every</em> platform</h2>
<p class="section-lede">Every program can be used three ways: from a command line that takes the original program's arguments, from Python and from Rust. Each port has a record that compares it with the original, case by case.</p>
</div>
</div>
<div class="features">
<div class="feature"><span class="label">Command line</span><h3>The original's arguments</h3><p><code>larmorx &lt;family&gt; &lt;program&gt; &lt;the original's arguments&gt;</code>, or <code>lx</code> for short, takes the original's options. How far the messages and exit statuses match is stated in each port's record.</p></div>
<div class="feature"><span class="label">Python</span><h3>Python calls</h3><p><code>import larmorx as lx</code>: the same programs, with typed options, on images in memory.</p></div>
<div class="feature"><span class="label">LARMORX's options</span><h3>Threads, port, defects</h3><p><code>--n-threads N</code>, <code>--implementation auto|replica|clean-room</code> and <code>--upstream-defects fix|reproduce</code> stand between <code>larmorx</code> and the family, from the next release; 0.1.0rc1 reads the environment variables they replace, <code>OMP_NUM_THREADS</code>, <code>LARMORX_IMPLEMENTATION</code> and <code>LARMORX_UPSTREAM_DEFECTS</code>. In Python they are the arguments <code>n_threads</code>, <code>implementation</code> and <code>upstream_defects</code>.</p></div>
<div class="feature"><span class="label">Rust</span><h3>No C, C++ or Fortran</h3><p>Pure Rust, with no C, C++ or Fortran libraries. Each Rust function's origin is recorded in its crate's <code>PROVENANCE.md</code>. Results do not depend on the thread count, and the maths functions come from correctly rounded ports of <a class="body-link" href="https://core-math.gitlabpages.inria.fr/">CORE-MATH</a> (the pure-Rust <code>libm</code> where not ported yet), so a program gives the same bits on every platform (<a class="body-link" href="{{ link('/concepts/why-rust-and-python/') }}">why Rust and Python</a>).</p></div>
<div class="feature"><span class="label">Platforms</span><h3>Six platforms, one output</h3><p>Continuous integration builds the wheels and runs the test suites on Linux (x86-64, aarch64), macOS (Intel, Apple silicon) and Windows (x64, arm64). The cross-platform checks test that every program gives its Linux x86-64 output bit for bit on each platform.</p></div>
<div class="feature"><span class="label">Validation</span><h3>Documented differences</h3><p>Every port has a record of its comparison with the original. Defects found in an original are registered and corrected by default (<code>fix</code>), with a warning; <code>upstream_defects="reproduce"</code> gives the original's behaviour, and the comparisons with the original run with it.</p></div>
</div>
<div class="try">
<div>

```bash
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

<p class="try-note">The command line takes the original programs' arguments; Python takes the same programs with typed options, on images in memory. A first session from start to end, on public data: <a class="body-link" href="{{ link('/getting-started/#first-steps') }}">First steps</a>.</p>

</section>

<section class="home-section" aria-labelledby="status">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">04</div>
<div>
<p class="kicker">Where it stands</p>
<h2 id="status">What is ported, and what is <em>planned</em></h2>
<p class="section-lede">The programs ported so far, each compared with its original (ANTs 2.6.5, AFNI 26.3.05, FSL 6.0.7.23, sdcflows 2.17.1, tedana 26.0.3) or, for LARMORX's own NIfTI reader and writer, with nibabel. Each name leads to its evidence page, with figures that compare its ports with the original; each line links to its records in the main repository. Everything else is planned.</p>
</div>
<p class="margin-note"><b>In the repository</b>API pages are in <a href="{{ repo('docs/api/') }}">docs/api</a>, benchmark reports in <a href="{{ repo('docs/benchmarks/') }}">docs/benchmarks</a>, and the defects found in the originals in the <a href="{{ repo('docs/findings/upstream-defects.md') }}">register</a>.</p>
</div>
<div class="status-head"><h3>Ported</h3><p>{{ data.status.implemented | length }} lines · the standard comparison</p></div>
<div class="table-wrap">
<table class="tools tools--grouped">
<thead><tr><th scope="col">Program</th><th scope="col">Ports</th><th scope="col">Validation</th></tr></thead>
{%- for g in data.programs.groups if not g.get('planned') %}
{%- set rows = data.status.implemented | selectattr('eco', 'equalto', g.id) | list %}
{%- if rows %}
<tbody class="eco-{{ g.id }}">
<tr class="grp"><th scope="colgroup" colspan="3"><span class="prog-chip">{{ g.name }}</span></th></tr>
{%- for row in rows %}
<tr><td><span class="tool-name">{% if row.page is defined %}<a href="{{ link(row.page) }}">{{ row.tool | md_inline }}</a>{% else %}<span>{{ row.tool | md_inline }}</span>{% endif %}</span><span class="tool-use">{% for u in row.use %}<code>{{ u }}</code>{% endfor %}</span></td><td class="how">{{ row.how | md_inline }}</td><td class="val">{{ row.validation | md_inline }}</td></tr>
{%- endfor %}
</tbody>
{%- endif %}
{%- endfor %}
</table>
</div>
<div class="status-head"><h3>Planned</h3><p>the next steps first, from the <a href="{{ link('/roadmap/') }}">roadmap</a></p></div>
<ol class="plan">
{%- for item in data.status.planned %}
<li><h3>{{ item.title }}</h3><p class="plan-eco">{% for e in item.eco %}<span class="eco-chip eco-{{ e }}">{{ eco[e].name }}</span>{% endfor %}</p><p>{{ item.text | md_inline }}</p></li>
{%- endfor %}
</ol>
<p class="status-note">Install it with <code>pip install larmorx</code>: the library and the <code>larmorx</code> and <code>lx</code> commands. <code>larmorx[prep]</code> adds what the larmorprepx pipeline will need, and <code>larmorx[all]</code> also the replicas of FSL's programs (<code>larmorx-nc</code>, non-commercial use only) and of tedana's <code>t2smap</code> (<code>larmorx-gpl</code>, GPL-3.0). Standalone programs, container images and what your computer needs: <a class="body-link" href="{{ link('/getting-started/') }}">Getting started</a>.</p>
</section>

<section class="home-section" aria-labelledby="philosophy">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">05</div>
<div>
<p class="kicker">The name</p>
<h2 id="philosophy">Named after the <em>Larmor</em> frequency</h2>
<p class="section-lede">The name comes from the Larmor frequency: in a magnetic field, spins of one kind precess at one frequency. LARMORX brings programs from different projects into one package and compares each with its original the same way.</p>
</div>
</div>
<div class="larmor">
<figure class="equation">
<span class="math" aria-label="omega equals gamma times B zero">ω = γ B<sub>0</sub></span>
<figcaption>the Larmor frequency: γ the gyromagnetic ratio, B<sub>0</sub> the field</figcaption>
</figure>
<div class="larmor-text">
<p>The name is inspired by the <strong>Larmor frequency</strong>, a fundamental concept in magnetic resonance imaging: in a uniform magnetic field B<sub>0</sub>, nuclear spins of the same species precess at the same frequency, ω = γB<sub>0</sub>.</p>
<p>LARMORX brings programs from different projects into one package for one purpose: <strong>FAIR</strong> research, research that is Findable, Accessible, Interoperable and Reusable.</p>
</div>
</div>
<ul class="fair" aria-label="FAIR, for research software">
<li><span class="letter" aria-hidden="true">F</span><h3>Findable</h3><p>A public repository with versioned history, releases on PyPI and GitHub, and citation metadata (<a class="body-link" href="{{ repo('CITATION.cff') }}">CITATION.cff</a>).</p></li>
<li><span class="letter" aria-hidden="true">A</span><h3>Accessible</h3><p>Open source under Apache-2.0; native wheels for six platforms that need no external neuroimaging installations, containers or administrator rights, and <a class="body-link" href="{{ link('/getting-started/') }}#containers">container images</a> for those who prefer them.</p></li>
<li><span class="letter" aria-hidden="true">I</span><h3>Interoperable</h3><p>Standard formats (NIfTI-1/2, ITK transform files including HDF5), the original programs' command-line arguments, and a Python API for pipelines.</p></li>
<li><span class="letter" aria-hidden="true">R</span><h3>Reusable</h3><p>A permissive licence, documentation for every program, provenance records, records of every comparison, case by case, and a register of the differences from the originals.</p></li>
</ul>
<p class="fair-source">The project follows the FAIR Principles for Research Software, <a class="body-link" href="https://doi.org/10.15497/RDA00068">FAIR4RS</a>.</p>
<div class="closing">
<p>How every port is compared with its original, and where the records are; how to install LARMORX and run its first programs.</p>
<div class="btn-row"><a class="btn btn--secondary" href="{{ link('/validation/') }}">Validation<svg aria-hidden="true"><use href="#i-arrow-right"/></svg></a><a class="btn btn--secondary" href="{{ link('/getting-started/') }}">Getting started<svg aria-hidden="true"><use href="#i-arrow-right"/></svg></a></div>
</div>
</section>
