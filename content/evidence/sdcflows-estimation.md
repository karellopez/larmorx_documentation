---
title: sdcflows' PEPOLAR, direct and fieldmap-less estimation
kicker: Evidence · sdcflows
lede: >-
  The rest of what fMRIPrep runs, through sdcflows, to estimate the field that corrects
  susceptibility distortion: PEPOLAR pairs through FSL's topup, direct field maps in Hz, the
  fieldmap-less estimation through ANTs' SyN registration, the brain masks of magnitudes and EPIs,
  the niworkflows and nipype pieces under them, fMRIPrep's own field-map steps, and sdcflows' BIDS
  app. LARMORX's port is a replica of sdcflows 2.17.1 and niworkflows 1.15.4, with the arithmetic
  of SciPy, scikit-image, numpy and nibabel, and pybids' dataset index. In `reproduce` it gives the
  originals' outputs bit for bit in each of the 57 cases of its six records. Its BIDS app writes
  sdcflows' derivative files, byte for byte, on the eight datasets of sdcflows' own runs, and its
  field-map stage, run as fMRIPrep ran it, gives fMRIPrep's own derivatives. Its default, `fix`,
  corrects the originals' defects or refuses them with a clear error, each with the original's
  result on request.
description: >-
  How LARMORX's replica of sdcflows' PEPOLAR, direct and fieldmap-less estimation, its masks, its
  BIDS app and fMRIPrep's own field-map steps compares with sdcflows 2.17.1, niworkflows, nipype,
  SciPy, scikit-image, numpy and fMRIPrep 25.2.6's own files: the BIDS app on two datasets of
  sdcflows' own runs, the fieldmap-less estimation beside ANTs' own band, the brain masks, SciPy's
  watershed corrected by default, the corrections, the step between library releases, random
  testing, every case of the records with its verdict, speed and memory.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crates <code>larmorx-sdcflows</code> and <code>larmorx-ndimage</code>; <code>lx.sdcflows</code>, <code>lx.niworkflows</code>, <code>lx.ndimage</code>, <code>lx.skimage</code>, <code>lx.bids</code> and larmorprepx's field-map stage, translated from sdcflows 2.17.1's estimation workflows (<code>init_topup_wf</code>, <code>init_fmap_wf</code>, <code>init_syn_preprocessing_wf</code>, <code>init_syn_sdc_wf</code>, <code>init_unwarp_wf</code>, <code>init_fmap_preproc_wf</code>, the 3dQwarp workflow's own steps), its masks, interfaces, estimator search and BIDS app, niworkflows 1.15.4's and nipype 1.12.0's pieces under them, fMRIPrep 25.2.6's own field-map steps and the SciPy 1.18.1, scikit-image 0.26.0 and numpy 2.5.4 routines they call</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span> (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/sdcflows-estimation.md') }}">standard comparison</a> (sdcflows 2.17.1), with its <a href="{{ repo('docs/validation/sdcflows-estimation-full.md') }}">full comparison</a> and the <a href="{{ repo('docs/validation/sdcflows-estimation-app-shared.md') }}">BIDS app in the shared environment</a> · <a href="{{ repo('docs/validation/ndimage-skimage.md') }}">SciPy, scikit-image and numpy</a> (with its <a href="{{ repo('docs/validation/ndimage-skimage-full.md') }}">full comparison</a>) · <a href="{{ repo('docs/validation/niworkflows-helpers.md') }}">niworkflows' helpers</a> · findings <a href="{{ repo('docs/findings/sdcflows-estimation.md') }}">sdcflows-estimation</a>, <a href="{{ repo('docs/findings/scipy-ndimage-filters.md') }}">scipy-ndimage-filters</a> · benchmark <a href="{{ repo('docs/benchmarks/sdcflows-estimation.md') }}">sdcflows-estimation</a></dd>
<dt>Reference</dt><dd><a href="{{ link('/programs/sdcflows/sdcflows/') }}"><code>sdcflows</code></a> · API pages <a href="{{ repo('docs/api/sdcflows-fieldmap.md') }}">sdcflows-fieldmap</a>, <a href="{{ repo('docs/api/niworkflows-helpers.md') }}">niworkflows-helpers</a>, <a href="{{ repo('docs/api/ndimage-filters.md') }}">ndimage-filters</a>, <a href="{{ repo('docs/api/skimage.md') }}">skimage</a>, <a href="{{ repo('docs/api/bids.md') }}">bids</a></dd>
</dl>

## What is compared {#what-it-is}

Echo-planar images are displaced along their phase-encoding axis wherever the main field is not uniform, by the local off-resonance frequency (in Hz) times the readout time. sdcflows (the NiPreps developers, Apache-2.0), the library fMRIPrep uses to estimate that field and correct the distortion, knows four kinds of estimator. The phase-difference field maps, the field-map model of B-splines and the unwarping are on [their own page](/evidence/sdcflows-fieldmap/). This page holds the other three and what surrounds them:

- **PEPOLAR**: two or more EPIs with opposite phase encoding (`dir-AP` and `dir-PA`). sdcflows' `init_topup_wf` regrids their volumes onto one grid, merges them and gives them to FSL's topup (its `b02b0` settings), reorients the field and its coefficients back, averages the corrected reference (niworkflows' `RobustAverage`, AFNI's 3dvolreg) and skull-strips it. Its other PEPOLAR workflow, `init_3dQwarp_wf`, is one sdcflows never chooses (its estimators run topup); its own Python steps are ported.
- **Direct field maps**: the scanner's map in Hz with its magnitude. `init_fmap_wf` merges them, skull-strips the magnitude (niworkflows' `IntensityClip`, ANTs' N4, sdcflows' `brain_masker`) and fits the field by sdcflows' B-splines.
- **Fieldmap-less (SyN)**: no field map at all. With `--use-syn-sdc`, fMRIPrep registers the BOLD reference to the anatomical image brought into its space with ANTs' SyN, the deformation restricted to the phase encoding and weighted by an atlas of where distortion occurs (`init_syn_preprocessing_wf`, `init_syn_sdc_wf`), and turns the displacements into a field.
- **Around them**: the estimators found in a BIDS dataset (sdcflows' `wrangler`, pybids' dataset index: `lx.bids`, without its database), `init_fmap_preproc_wf` with its derivatives and reports' data sinks (niworkflows' `DerivativesDataSink`), the field map's registration to the EPI and `init_unwarp_wf`, fMRIPrep 25.2.6's own field-map steps (the estimators it selects, the BOLD fit's field-map nodes), and sdcflows' BIDS app (`sdcflows <bids> <out> participant`).

The replica runs beside the originals, run in-process: sdcflows 2.17.1 with nipype 1.12.0, niworkflows, SciPy, scikit-image and numpy, and sdcflows' BIDS app whole. fMRIPrep's own graphs, files and command lines are those of its runs, with sdcflows 2.15.1 and niworkflows 1.15.2 in fMRIPrep 25.2.6's image.

```bash
larmorx sdcflows sdcflows /data/bids /data/out participant --participant-label 01
```

```python
import larmorx as lx

# a PEPOLAR estimator: topup on an AP/PA pair, the field and its coefficients
est = lx.sdcflows.topup_workflow(
    ["sub-01_dir-AP_epi.nii.gz", "sub-01_dir-PA_epi.nii.gz"],
    [{"PhaseEncodingDirection": "j-", "TotalReadoutTime": 0.05},
     {"PhaseEncodingDirection": "j", "TotalReadoutTime": 0.05}],
    out_dir="work", n_threads=8,
)
# the fieldmap-less estimation from syn_preprocessing_workflow's outputs
metadata = {"PhaseEncodingDirection": "j-", "TotalReadoutTime": 0.0315}
syn = lx.sdcflows.syn_sdc_workflow(
    ("boldref.nii.gz", metadata), "boldref_mask.nii.gz", "anat_in_epi.nii.gz",
    "anat_mask_in_epi.nii.gz", "prior_in_epi.nii.gz", out_dir="work", n_threads=8,
)
# sdcflows' BIDS app, as on its command line
lx.sdcflows.run_app(["/data/bids", "/data/out", "participant", "--participant-label", "01"])
```

The [API pages](repo:docs/api/sdcflows-fieldmap.md) describe every function and option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its port {#ports}

sdcflows, niworkflows, nipype, pybids, scikit-image, SciPy and numpy are permissive (Apache-2.0, MIT, BSD-3-Clause), so the replica is in `larmorx` itself. Their Python is the specification, with the arithmetic of the library releases they call.

- The workflows are plain Python functions, with no nipype and no graph engine. Each node writes its files into the folder nipype would give it (`out_dir/<workflow>/<node>`), so a run can be compared with sdcflows' file by file, and every command line is nipype's.
- The programs underneath run through LARMORX's own replicas: FSL's topup and PRELUDE (`lx.fsl`), ANTs' registration, N4, ImageMath and antsApplyTransforms (`lx.ants`), AFNI's 3dvolreg (`lx.afni.volreg`).
- The numeric routines run in Rust: SciPy's ndimage filters, morphology, labels and watershed, scikit-image's random walker and Otsu threshold (`larmorx-ndimage`), numpy's percentiles, sums and dot products in the order of the kernels numpy calls, and SciPy's 4 × 4 inverse with its condition estimate (`larmorx-transform`). Every sum is in the original's order, so `n_threads` never changes a bit.

A clean room of these steps is planned after FreeSurfer ([roadmap](/roadmap/)).

## The verdicts at a glance {#verdicts}

The replica is a translation of the originals' source, so the question is whether it gives their bytes.

{{ ev.agreement('sdcflows-estimation', 'port') }}

The records run the originals in-process as the reference: sdcflows 2.17.1 with nipype 1.12.0, niworkflows, SciPy, scikit-image and numpy; sdcflows' BIDS app whole; fMRIPrep 25.2.6's own graphs, files and command lines of its runs. They run in two Python environments:

- the newest library releases (numpy 2.5.4 with OpenBLAS 0.3.34, SciPy 1.18.1), LARMORX's reference;
- the releases the other comparisons share (numpy 2.3.5, SciPy 1.15.3).

They compare the replica with them in `reproduce` (`upstream_defects="reproduce"`): every array, file (decompressed), header, warning, message, command line and exit status, bit for bit. The 57 cases of the six records pass, with 1,753 checks. Each case is one of the comparison's check scripts (or one of its sections) run as a process of its own, one check per line it prints.

{{ ev.table('sdcflows-estimation', 'records') }}

## sdcflows' BIDS app: PEPOLAR and a direct field map {#app}

sdcflows' own command line runs its estimation on a BIDS dataset: it finds the estimators, runs each one's workflow and writes its derivatives (the field in Hz, its coefficients, the reference and its brain mask, their sidecars). Both examples below run it whole, on two datasets of sdcflows' own runs:

- sdcflows 2.17.1 at one thread, with the programs underneath through the cache of the original's runs;
- the replica (`larmorx sdcflows sdcflows`, `lx.sdcflows.run_app`) at one thread, with LARMORX's own replicas underneath, and again at 14 threads in `fix` and in `reproduce`.

fMRIPrep 25.2.6 ran the same estimators on the same data. Its own derivatives are compared with the replica's field-map stage run as fMRIPrep ran it (sdcflows 2.15's PEPOLAR wiring, its image's numpy 2.2.6 and SciPy 1.15.2). sdcflows' own run at four threads is the original's own spread.

The input panels are the raw images. The outputs, chosen above the viewer, are the field map in Hz, the reference (the corrected EPI or the magnitude), the masker's brain probability and the brain mask over the input. The viewer opens on the field map.

### ds006736: a PEPOLAR pair through topup {#pepolar}

{{ ev.example('sdcflows-estimation', 'app-ds006736') }}

### ds005752: a direct field map in Hz {#direct}

{{ ev.example('sdcflows-estimation', 'app-ds005752') }}

### The app on the eight datasets of sdcflows' own runs {#app-runs}

The records' cases run the app whole on every dataset of sdcflows' own runs (2026-11-08): a direct field map, phase differences (two at 1.5 T; one at 7 T, named by its `B0FieldIdentifier`; Philips' with two PEPOLAR estimators beside it), PEPOLAR pairs and multiband series. Every derivative file is sdcflows', byte for byte, with the newest releases and with the shared ones; the times are the benchmark's.

{{ ev.table('sdcflows-estimation', 'app-runs') }}

### fMRIPrep's own field-map derivatives {#stage}

larmorprepx's field-map stage (`estimate_fieldmaps`), run with fMRIPrep 25.2.6's options on five of its runs, gives fMRIPrep's own derivatives. Of their 36 NIfTI files:

- 13 are identical;
- 13 hold identical data with only FSL's build string in the header's `descrip` (fMRIPrep's image runs FSL 2501.4, LARMORX's replicas FSL 6.0.7.23);
- 10 follow an N4 node that ANTs reproduces at the node's 8 threads with glibc's maths (fMRIPrep's file) and at one thread with correctly rounded maths (the replica's).

{{ ev.table('sdcflows-estimation', 'stage') }}

## The fieldmap-less (SyN) estimation {#syn}

With `--use-syn-sdc` and no field map, fMRIPrep 25.2.6 estimates the field from the BOLD reference and the anatomy:

- sdcflows' `init_syn_preprocessing_wf` brings the anatomical image, its brain mask and an atlas of where distortion occurs into the EPI's space;
- `init_syn_sdc_wf` registers the clipped BOLD reference to that anatomy with ANTs' SyN (two Mattes metrics on each side, the image and its normalised Laplacian; the deformation restricted to the phase-encoding axis);
- it turns the displacements along that axis into Hz, resamples them onto the EPI's grid, fits sdcflows' B-splines and unwarps the reference.

The records check every node of fMRIPrep's five SyN estimators (three fMRIPrep runs) on its own inputs, and sdcflows' own graphs run by nipype, file by file (105 of 105 files of the preprocessing, 19 of 19 of the estimation), with ANTs at one thread.

The replica's registration computes ANTs' one-thread result at any thread count, with correctly rounded maths. On fMRIPrep's own inputs and seed for ds000228's estimator (a child of 3.5 years), its warp is ANTs 2.6.5's at one thread with CORE-MATH's functions preloaded, byte for byte, and so is every output after it.

fMRIPrep ran the registration at four threads with glibc's maths, and ANTs' result depends on both. Its Mattes metrics sum their joint histograms per work unit, so at four threads the field moves by up to 1.70 Hz from the one-thread run's, and there ANTs 2.6.5 does not even repeat itself (two runs of fMRIPrep's command, up to 0.70 Hz apart). glibc's maths moves it by up to 0.016 Hz at one thread. fMRIPrep's own field lies at most 1.80 Hz from the replica's, within ANTs 2.6.5's own band for this call (up to 1.82 Hz between two of its runs with glibc's maths), in a field of −25.6 to 40.8 Hz inside the brain.

The replica's default, `fix`, corrects ITK-31 here (the first SyN stage has a fixed mask only, and ITK keeps a stale mask for the role without one), which moves the field by up to 0.82 Hz. The example places fMRIPrep's own field against ANTs' own band for this call: ANTs 2.6.5 ran fMRIPrep's command at one thread with each maths and twice at four threads with glibc's, each warp followed by sdcflows' steps.

{{ ev.example('sdcflows-estimation', 'syn-ds000228') }}

## The brain masks {#masks}

### A magnitude's brain mask: brain_masker {#masker}

sdcflows' `brain_masker` skull-strips every magnitude and every PEPOLAR reference fMRIPrep estimates a field from. On fMRIPrep's own input of its ds002603 call, the replica's probability, mask and masked magnitude are sdcflows', every value. Run on fMRIPrep's image's libraries (numpy 2.2.6, SciPy 1.15.2), they are fMRIPrep's own files.

{{ ev.example('sdcflows-estimation', 'masker-ds002603') }}

### An EPI's mask, and SciPy's watershed corrected by default {#epi-mask}

sdcflows' `epi_mask` (no workflow of sdcflows or fMRIPrep calls it) floods the EPI from two markers with SciPy's `watershed_ift`. SciPy's watershed reaches neighbours across the image's edges (SCI-13) and can leave an element alone in its queue (SCI-14), so the object's region stops early. The replica's default, `fix`, corrects both and names them; in `reproduce` it gives SciPy's mask. The corrected masks agree better with fMRIPrep's own brain masks on three of the four BOLD references and the same on the fourth, worse on none (rule A).

{{ ev.example('sdcflows-estimation', 'epi-mask-ds003592') }}

{{ ev.table('sdcflows-estimation', 'epi-mask') }}

## Corrections by default {#corrections}

Every defect the replica found in the originals was decided by the register's rules (A: corrected by default; B: refused with a clear error; C: kept and documented; D: measured first). `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives the original's behaviour, its errors and warnings included, where LARMORX has a switch ([findings](repo:docs/findings/sdcflows-estimation.md), [register](repo:docs/findings/upstream-defects.md)).

- 89 entries were registered: 35 in sdcflows, 23 in niworkflows, nipype, pybids and fMRIPrep, 27 in SciPy and 4 in scikit-image.
- 42 are corrected by default and 15 refused with a clear error. The others are kept and documented, measured first, or concern a part LARMORX does not run (its database, its reports).
- 61 have the switch; crashes, memory errors and nondeterminism are never reproduced.
- 19 reach fMRIPrep's own calls (the table's fifth column).

{{ ev.table('sdcflows-estimation', 'corrections') }}

## The originals' own step: two library releases {#step}

Each comparison of the library scripts also runs the originals with the releases the other comparisons share (numpy 2.3.5 with OpenBLAS 0.3.30, SciPy 1.15.3) and says what changed from them to the newest, line by line. Of 303 compared lines 127 change, each for a known reason:

- SciPy 1.18 rewrote `scipy.linalg.inv`;
- SciPy 1.16 sorts every row of a sparse matrix built through COO (scikit-image's random walker then sums its conjugate gradients in another order);
- numpy 2.4 and 2.5 changed their scalar arithmetic and percentile's argument check;
- numpy's OpenBLAS 0.3.31 and later bundle LAPACK 3.12.1.

The replica follows each release.

{{ ev.table('sdcflows-estimation', 'step') }}

## Speed {#speed}

The benchmark ([report](repo:docs/benchmarks/sdcflows-estimation.md)) runs the originals in-process and the replica on the memory rule's four calls (fMRIPrep's real inputs) and sdcflows' BIDS app on five datasets of its own runs, every output checked byte for byte.

- At one thread the replica takes 0.86 to 2.97 times the originals' speed on the four calls (`IntensityClip` and `RobustAverage`'s own steps are a little slower), 1.16 to 7.42 times at 14.
- The BIDS app runs 1.2 to 5.3 times faster at one thread, its programs run fresh.
- On random testing's random walker whose system is NaN from its first iteration, scikit-image's conjugate gradients run to their limit (22 s); the replica stops with the same solution once nothing can change it (0.05 s).

{{ ev.speed('sdcflows-estimation') }}

## Memory {#memory}

The memory rule allows LARMORX at most 10 % above the original's peak plus 8 MiB for the same call; here the replica needs 16 to 72 % of the original's peak.

{{ ev.table('sdcflows-estimation', 'memory') }}

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the originals and the replica and compares every output ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a permanent case, registered as a defect of the original, or reported. The replica's two random-testing runs of 2026-11-09 drew 312,081 cases, the second with numpy's AVX-512 kernels off; every compared case agrees. The 17 differences of the shorter runs before them are triaged below: 9 mistakes of the replica's fixed, each with a permanent case, 5 defects of the originals registered, 3 mistakes of the test harness.

{{ ev.table('sdcflows-estimation', 'trial') }}

{{ ev.table('sdcflows-estimation', 'triage') }}

## Every case {#cases}

Each case of the records, with what it tests, its command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('sdcflows-estimation') }}

## Known limits {#limits}

- sdcflows' `init_3dQwarp_wf` (the other PEPOLAR workflow, which sdcflows never chooses and fMRIPrep's image cannot run) needs AFNI's 3dQwarp, FreeSurfer's `mri_robust_template` and niworkflows' `init_enhance_and_skullstrip_bold_wf`, not ported yet. `lx.sdcflows.qwarp_workflow` stops with an error naming them (SDC-23); its own Python steps are ported and checked.
- sdcflows' reports (its reportlets) are larmorprepx's, with the pipeline's reports.
- fMRIPrep's BOLD steps that use the field (`B0FieldTransform` in its resampler) are on [their own page](/evidence/resample-series/); the rest of fMRIPrep's BOLD workflow comes with larmorprepx.
- The comparisons with fMRIPrep stage by stage come once every tool is ported.

## History {#history}

- **2026-11-08**: sdcflows 2.17.1's own BIDS app run on the eight datasets of its own runs, the reference of the app's cases.
- **2026-11-09**: the replica's six records and its two random-testing runs, 312,081 cases.
- **2026-11-10**: the replica of PEPOLAR, direct and fieldmap-less estimation, sdcflows' masks and BIDS app, niworkflows' helpers, the BIDS index and fMRIPrep's field-map steps complete ([the roadmap](/roadmap/)).
