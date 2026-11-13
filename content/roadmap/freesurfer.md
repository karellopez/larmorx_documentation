---
title: FreeSurfer's roadmap
kicker: Roadmap
lede: How LARMORX ports FreeSurfer 8.2.0, step by step. Every program recon-all runs, in the order it runs them, the waves the work is done in, where each wave stands, and how each program is checked against FreeSurfer.
description: The plan for FreeSurfer 8.2.0 in LARMORX — a replica and a clean room of every program recon-all runs in both its streams (classic and FreeSurfer 8's networks), and of fMRIPrep's FreeSurfer programs; recon-all's steps in order, each with its programs and its wave; the waves from the preparation to recon-all, their size and their status for the replica and the clean room; how each program is validated; FreeSurfer's reference runs.
evidence: true
wide: true
---
{##
  The statuses come from data/freesurfer-roadmap.yml (its header says how to update it); this
  page holds the description, which changes only when the plan does. Names of programs and
  stages only: nothing taken from FreeSurfer's source.
##}
{%- set fr = data['freesurfer-roadmap'] %}
{%- set words = {'done': 'done', 'in-progress': 'in progress', 'next': 'next', 'planned': 'planned'} %}
{%- macro st(s) -%}
{%- set w = (s or 'planned').split(' ') -%}
{%- if w[0] == 'none' -%}<span class="rm-none">none</span>
{%- else -%}<span class="rm-status rm-status--{{ w[0] }}">{{ words[w[0]] }}</span>{% if w | length > 1 %} <span class="rm-date">{{ w[1] }}</span>{% endif %}
{%- endif -%}
{%- endmacro %}
{%- macro wv(id) -%}<a href="#wave-{{ id | replace('.', '-') | lower }}">{{ id }}</a>{%- endmacro %}

**Last updated: {{ fr.updated }}.** FreeSurfer 8.2.0 is the step under way on the [roadmap](/roadmap/#next). Its statuses below change at every merge of its work; the plan behind them is in the repository's [FreeSurfer plan](repo:docs/freesurfer-plan.md).

## What this step delivers {#delivers}

- **Every program `recon-all` runs, ported twice:** a replica in the package `larmorx-freesurfer`, under FreeSurfer's licence, and a clean room in `larmorx`, under Apache-2.0, built for speed (FreeSurfer is the slowest part of fMRIPrep's preprocessing). Each port is complete: every option, message, exit status and failure case, with the originals' defects corrected by default and reproduced on request, as for every program on this site ([Concepts](/concepts/#defects)).
- **Both of `recon-all`'s streams** (below) and **`recon-all` itself**, in both ports.
- **The FreeSurfer programs fMRIPrep and sMRIPrep run outside `recon-all`** ([the list](#fmriprep)).
- **The code FreeSurfer borrows from other projects**, each piece with a replica in the package of its own licence (GSL's random-number generators in `larmorx-gpl`, `tkregister2_cmdl` as a program of its own in `larmorx-nc`) and a clean room in `larmorx`. Washington University's Talairach tools get a clean room only: their terms do not allow a replica without the university's written permission.
- **No licence key:** FreeSurfer's key is a check inside FreeSurfer's own programs, which the ports do not need.
- **FreeSurfer's data files** (atlases, colour tables, the average subject `fsaverage`, the networks' weights): those up to 2 MB shipped in `larmorx-freesurfer`, the larger ones (FreeSurfer's atlases are about 650 MB) fetched on first use from FreeSurfer's own public store and checked by their SHA-256, or read from a FreeSurfer installation (`FREESURFER_HOME`). A list of every file, with its licence, comes with the foundations.

### Two streams {#streams}

`recon-all` 8.2.0 runs, by default, the **v8 stream**: the brain mask by SynthStrip, the brain's labels by SynthSeg and the registration by SynthMorph, three neural networks, with several new correction steps. Its `-no-v8` flag gives the **classic stream**, what fMRIPrep 25's FreeSurfer 7.3.2 runs: the watershed skull strip, the Talairach registration, the atlas' subcortical labels. Most programs, every surface step among them, belong to both streams. The work goes in that order: the programs both streams run first, then the classic stream's own, with the v8 stream's networks as a track of their own beside them. FreeSurfer 7.3.2 is not ported; the final comparisons with fMRIPrep use it as a reference.

## Where it stands {#status}

<div class="rm-stack rm-waves">

| Wave | Pieces of work: replica / clean room | Replica | Clean room |
|---|---|---|---|
{%- for w in fr.waves %}
| <a href="#wave-{{ w.id | replace('.', '-') | lower }}">{{ w.id }} {{ w.name }}</a> | {% if w.get('size') %}{{ w.size.replica }} / {{ w.size.clean_room }}{% else %}–{% endif %} | {% if w.get('status') %}{{ st(w.status) }}{% else %}{{ st(w.replica) }}{% endif %} | {% if w.get('status') %}one step for both{% else %}{{ st(w.clean_room) }}{% endif %} |
{%- endfor %}

</div>

In all, 229 pieces of work for the replicas and 129 for the clean rooms (13 of them the clean rooms of the borrowed permissive code, which come after FreeSurfer with the [other permissive ports' clean rooms](/roadmap/#next)), about 309,000 lines of FreeSurfer's functions to follow, 90,000 of them the foundations (upper bounds: every line the programs can reach). The clean rooms follow one wave behind the replicas, written separately from descriptions of the programs' behaviour and from runs of FreeSurfer, never from its source. "Done" means its part's tests pass and it is merged; the extensive evidence comes in the [final validation phase](/roadmap/#final).

## `recon-all`'s steps, in order {#steps}

`recon-all -all` runs three parts: *autorecon1*, from the T1-weighted image to the brain without the skull; *autorecon2*, from the atlas registration to the white surface; *autorecon3*, from the sphere to the parcellations and the statistics. The steps on surfaces run for the left hemisphere, then for the right. Each step is named as `recon-all`'s log names it where it has a name; a program that a step's script runs inside it is listed in its [wave](#waves). *Stream*: *both*, or only the *v8* or the *classic* stream. *Wave*: the wave its port belongs to.

### Before the first step {#before}

<div class="rm-stack rm-steps">

| Step | Programs | What it does | Stream | Wave |
|---|---|---|---|---|
| Configuration and checks | `rca-config`, `rca-config2csh`, `fsr-getxopts`, `fs-check-version`, `fs-check-os` | Reads `recon-all`'s configuration and expert options, checks FreeSurfer's version and the operating system. | both | {{ wv('3.7') }}, {{ wv('3.5') }} |

</div>

### autorecon1 {#autorecon1}

<div class="rm-stack rm-steps">

| Step | Programs | What it does | Stream | Wave |
|---|---|---|---|---|
| Input | `mri_convert`, `mri_info` | Converts the T1-weighted image into FreeSurfer's MGZ format. | both | {{ wv('3.2') }} |
| Motion correction (MotionCor) | `mri_robust_template`, `mri_convert`, `mri_add_xform_to_header`, `lta_convert` | Averages the T1-weighted images into one when there are several, resamples it to FreeSurfer's conformed grid (256 × 256 × 256 voxels of 1 mm) and writes the transform between the two. | both | {{ wv('3.2') }} |
| Brain mask by network | `mri_synthstrip` | SynthStrip, a neural network, draws the brain mask. | v8 | {{ wv('N') }} |
| Labels by network | `mri_synthseg`, `csvprint` | SynthSeg, a neural network, labels the brain's structures and measures their volumes, the intracranial volume among them. | v8 | {{ wv('N') }} |
| Talairach | `mri_nu_correct.mni`, `talairach_avi`, `lta_convert` | Corrects the intensity bias, then registers the head to the MNI305 atlas with an affine transform. | classic | {{ wv('3.2') }}, {{ wv('3.6') }} |
| Talairach failure detection | `talairach_afd`, `extract_talairach_avi_QA.awk` | Checks the transform against those of known good registrations. After a failure the registration runs again with another atlas, and after a second one with MINC's `talairach` ([later](#later)). | classic | {{ wv('3.6') }} |
| Talairach, by the v8 stream | `rca-talairach` | Registers the head to the MNI305 atlas, from the network's brain mask. | v8 | {{ wv('N') }} |
| Registration by network | `fs-synthmorph-reg` | SynthMorph, a neural network, registers the head to the MNI152 template, nonlinearly. | v8 | {{ wv('N') }} |
| Intensity correction (Nu Intensity Correction) | `mri_nu_correct.mni` with ITK's N4 (`AntsN4BiasFieldCorrectionFs`), `mri_add_xform_to_header` | Removes the slow change of intensity across the image that the scanner's coils cause (N4) and rescales the image to 8 bits (`nu.mgz`). | both | {{ wv('3.2') }} |
| Intensity normalization | `mri_normalize` | Scales the intensities so that white matter is 110 everywhere (`T1.mgz`). | both | {{ wv('3.2') }} |
| Dura and venous sinuses | `mri_mcadura_seg`, `mri_vsinus_seg` | Neural networks label parts of the dura (`mca-dura.mgz`) and the venous sinuses (`vsinus.mgz`), so that the surfaces later stay out of them. | v8 | {{ wv('N') }} |
| Skull stripping, by the v8 stream | `mri_mask` | Applies the network's brain mask to the normalised image (`brainmask.mgz`). | v8 | {{ wv('3.2') }} |
| Skull stripping | `mri_em_register`, `mri_watershed` | Registers the head to an atlas that includes the skull, then strips the skull with the watershed method, guided by that atlas (`brainmask.mgz`). | classic | {{ wv('3.3') }}, {{ wv('3.6') }} |

</div>

### autorecon2 {#autorecon2}

<div class="rm-stack rm-steps">

| Step | Programs | What it does | Stream | Wave |
|---|---|---|---|---|
| EM registration | `mri_em_register` | Registers the brain to FreeSurfer's probabilistic atlas of brain structures, with an affine transform. | both | {{ wv('3.3') }} |
| CA normalize | `mri_ca_normalize` | Normalises the intensities again, with the intensity the atlas expects of each structure (`norm.mgz`). | both | {{ wv('3.3') }} |
| CA registration | `mri_ca_register` | Registers the brain to the atlas nonlinearly. | classic | {{ wv('3.3') }} |
| Entorhinal white matter | `mri_entowm_seg` | A neural network labels the white matter near the entorhinal cortex, which the next steps use to correct the white matter there. | v8 | {{ wv('N') }} |
| Subcortical segmentation | `mri_ca_label` | Labels the subcortical structures from the atlas and the registration (`aseg`). | classic | {{ wv('3.6') }} |
| Corpus callosum | `seg2cc`, `mri_cc` | Labels the corpus callosum in the segmentation. | both | {{ wv('3.2') }} |
| Intensity normalization 2 | `mri_normalize` | Normalises the intensities once more, with the segmentation (`brain.mgz`). | both | {{ wv('3.2') }} |
| Mask for the surfaces | `mri_mask`, `mri_edit_wm_with_aseg` | Masks the brain for the surfaces' placement; in the v8 stream also masks out the dura and the venous sinuses. | both | {{ wv('3.2') }} |
| White-matter segmentation | `AntsDenoiseImageFs`, `mri_segment`, `mri_edit_wm_with_aseg`, `mri_pretess` | Denoises the brain (ITK's non-local means), labels the white matter by its intensity and corrects that label with the segmentation (`wm.mgz`). | both | {{ wv('3.2') }} |
| Fill | `mri_fill` | Separates the two hemispheres and cuts away the brainstem and the cerebellum (`filled.mgz`). | both | {{ wv('3.2') }} |
| Tessellation | `mri_pretess`, `mri_tessellate`, `mris_extract_main_component` | Turns each hemisphere's filled volume into a first surface of triangles, kept to its largest piece. | both | {{ wv('3.4') }} |
| Smoothing, inflation, quick sphere | `mris_smooth`, `mris_inflate`, `mris_sphere` | Smooths that surface, inflates it and maps it quickly onto a sphere, for the topology fix. | both | {{ wv('3.4') }} |
| Topology fix | `mris_fix_topology`, `mris_euler_number`, `mris_topo_fixer`, `defect2seg`, `mris_remesh`, `mris_remove_intersection` | Removes the surface's holes and handles so that it has a sphere's topology (`mris_topo_fixer` only where a defect remains), records the defects as a volume, remeshes the surface into regular triangles and removes the places where it crosses itself. | both | {{ wv('3.4') }} |
| Grey and white intensities | `mris_autodet_gwstats` | Measures the intensities of grey and white matter near the surface. | both | {{ wv('3.5') }} |
| White surface, first placement | `mris_place_surface` | Moves the surface to the boundary between white and grey matter. | both | {{ wv('3.5') }} |
| Cortex label | `label-cortex`, `mri_label2label` | Labels the cortex on the surface, without and with the hippocampus and the amygdala. | both | {{ wv('3.5') }}, {{ wv('3.4') }} |
| Smoothing, inflation, curvature | `mris_smooth`, `mris_inflate`, `mris_curvature` | Smooths and inflates the white surface again (with the depth of the sulci) and computes its curvatures. | both | {{ wv('3.4') }}, {{ wv('3.5') }} |

</div>

### autorecon3 {#autorecon3}

<div class="rm-stack rm-steps">

| Step | Programs | What it does | Stream | Wave |
|---|---|---|---|---|
| Sphere | `mris_sphere` | Maps the inflated surface onto a sphere. | both | {{ wv('3.4') }} |
| Surface registration | `rca-surfreg`, `mris_register` | Registers the sphere to FreeSurfer's atlas of cortical folding. | both | {{ wv('3.5') }} |
| Jacobian and average curvature | `mris_jacobian`, `mrisp_paint` | Measures how much the registration stretches the surface, and maps the atlas' average curvature onto it. | both | {{ wv('3.5') }} |
| Cortical parcellation | `mris_ca_label` | Divides the cortex into regions from the atlas (Desikan-Killiany). | both | {{ wv('3.5') }} |
| White and pial surfaces | `mris_place_surface` | Places the final white surface and the pial surface, the outer boundary of the grey matter. | both | {{ wv('3.5') }} |
| Curvature, area, thickness, volume | `mris_place_surface`, `vertexvol`, `mris_curvature_stats` | Computes the curvature, area, thickness and volume at every vertex, and the curvatures' statistics. | both | {{ wv('3.5') }} |
| Cortical ribbon | `mris_volmask` | Fills the volume between the white and pial surfaces (`ribbon.mgz`). | both | {{ wv('3.5') }} |
| Parcellations 2 and 3 | `mris_ca_label` | The Destrieux (a2009s) and DKT parcellations. | both | {{ wv('3.5') }} |
| White and grey contrast | `pctsurfcon` | Measures the contrast between white and grey matter along the surface. | both | {{ wv('3.5') }} |
| Hypointensities | `mri_relabel_hypointensities` | Labels hypointensities of the white matter, with the white surfaces. | both | {{ wv('3.5') }} |
| Segmentations from the surfaces | `mri_surf2volseg`, `mri_brainvol_stats` | Corrects the segmentation with the surfaces (`aseg.mgz`), labels the cortex and the white matter by region (`aparc+aseg.mgz`, its two variants and `wmparc.mgz`) and measures the brain's volumes. | both | {{ wv('3.5') }} |
| Statistics | `mri_segstats`, `mris_anatomical_stats` | Writes the statistics of every structure and every cortical region (`aseg.stats`, `wmparc.stats`, the parcellations' statistics). | both | {{ wv('3.2') }}, {{ wv('3.5') }} |
| Brodmann areas | `mri_label2label`, `mris_label2annot`, `mris_anatomical_stats` | Maps the Brodmann areas and other labels of FreeSurfer's average subject (`fsaverage`) onto the subject, with their statistics. | both | {{ wv('3.4') }}, {{ wv('3.5') }} |

</div>

### fMRIPrep's programs outside `recon-all` {#fmriprep}

fMRIPrep and sMRIPrep run these FreeSurfer programs themselves. They belong to no stream and come with the waves their code belongs to, the volume ones early.

<div class="rm-stack rm-fmriprep">

| Program | What fMRIPrep does with it | Wave |
|---|---|---|
| `mri_coreg` | Registers the BOLD reference to the T1-weighted image: the start of the boundary-based registration. | {{ wv('3.2') }} |
| `mri_robust_template`, `mri_robust_register` | Average several T1-weighted images into one, and register two images robustly. | {{ wv('3.2') }} |
| `mri_vol2vol`, `lta_convert` | Resample a volume through a transform, and convert transform files between formats. | {{ wv('3.2') }} |
| `bbregister`, with `mri_segreg` and `tkregister2_cmdl` | Registers the BOLD reference to the white surface by the contrast across it (boundary-based registration). | {{ wv('3.5') }} |
| `mri_vol2surf`, `mri_surf2surf` | Sample a volume onto a surface, and resample data from one surface to another (`fsaverage`, `fsnative`). | {{ wv('3.5') }} |
| `mris_convert`, `mris_expand` | Convert surfaces to GIFTI, and make the mid-thickness surface. | {{ wv('3.5') }} |

</div>

## The waves {#waves}

Each wave delivers its programs complete: the replica first, its clean room one wave behind. A wave's pieces of work appear below with their own status as they begin.
{% for w in fr.waves %}
### {{ w.id }} {{ w.name }} {#wave-{{ w.id | replace('.', '-') | lower }}}

{{ w.delivers }}

<dl class="facts rm-facts">
{%- if w.get('status') %}
<dt>Status</dt><dd>{{ st(w.status) }}</dd>
{%- else %}
<dt>Replica</dt><dd>{{ st(w.replica) }}{% if w.get('replica_note') %} {{ w.replica_note | md_inline }}{% endif %}</dd>
<dt>Clean room</dt><dd>{{ st(w.clean_room) }}{% if w.get('clean_room_note') %} {{ w.clean_room_note | md_inline }}{% endif %}</dd>
{%- endif %}
{%- if w.get('size') %}
<dt>Size</dt><dd>{{ w.size.replica }} pieces of work for the replica, {{ w.size.clean_room }} for the clean room</dd>
{%- endif %}
{%- if w.get('programs') %}
<dt>Programs</dt><dd>{% for p in w.programs %}<code>{{ p }}</code>{% if not loop.last %}, {% endif %}{% endfor %}</dd>
{%- endif %}
</dl>
{% if w.get('parts') %}
<div class="rm-stack rm-parts">

| Part | What it holds | Replica | Clean room |
|---|---|---|---|
{%- for p in w.parts %}
| {{ p.name }} | {{ p.what }}{% if p.get('note') %} {{ p.note }}{% endif %} | {{ st(p.replica) }} | {{ st(p.clean_room) }} |
{%- endfor %}

</div>
{% endif %}
{%- endfor %}

### Later {#later}

Programs that no default path of either stream runs, ported after the waves:
{% for l in fr.later %}
- `{{ l.program }}`: {{ l.when }}.
{%- endfor %}

## How each program is validated {#validation}

Each program, replica and clean room, is checked in its own part, with the same depth as every port since 2026-10-28 ([levels of testing](/validation/#levels)):

- **The replay on every recorded head.** For each step of FreeSurfer's [reference runs](#runs), a replay tool rebuilds the subject's folder as it was before that step, runs the port there and compares what it writes with what FreeSurfer wrote, and with FreeSurfer's same step run again at one thread. Its comparisons understand FreeSurfer's files: MGZ volumes, surfaces, labels, annotations, transforms and the text files. So each program is tested on real heads without running `recon-all` again. The tool was proved on 68 recorded steps of both streams before any port.
- **The foundations, function by function**, against FreeSurfer's own library, built from 8.2.0 as the official release was.
- **Synthetic cases** for every option, message and failure case.
- **Golden cases**, so that the six platforms give the same results as Linux: volumes of at most 32 × 32 × 32 voxels, small synthetic surfaces.
- **The defects of FreeSurfer** found on the way, each decided by the four rules ([Concepts](/concepts/#defects)) and recorded in the repository's register.
- **Its record**, its memory near FreeSurfer's (at most 10 % and 8 MiB more) and its pages on this site: a reference page and an evidence page.

The extensive evidence, the whole [data panel](/validation/data-panel/), long random-testing runs and the comparisons with fMRIPrep, comes in the [final validation phase](/roadmap/#final).

## The reference runs {#runs}

FreeSurfer 8.2.0's own package, run without changes on six heads of the [data panel](/validation/data-panel/) chosen for their variety: a healthy adult at 3 T (ds000005), an older adult at 1.5 T (ds002422), a child of 3.5 years (ds000228), a 7 T MP2RAGE image (ds005454), a glioma (ds005003) and an older adult with head motion (ds004173). Each is run in both streams with `recon-all -all`, its steps one after the other, and every step is recorded: its command line, its times and threads, its exit status, and every file it reads, writes and deletes, kept once by its SHA-256.

<div class="rm-stack rm-runs">

| Runs | What they are | Status |
|---|---|---|
{%- for r in fr.runs %}
| {{ r.name }} | {{ r.what }} | {{ st(r.status) }} |
{%- endfor %}

</div>
