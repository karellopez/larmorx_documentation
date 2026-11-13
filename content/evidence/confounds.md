---
title: fMRIPrep's confound estimation
kicker: Evidence · fMRIPrep
lede: >-
  The confounds fMRIPrep computes for every BOLD run: its `desc-confounds_timeseries.tsv` and the
  JSON beside it, with CompCor, DVARS, framewise displacement, the motion parameters and their
  expansion, the tissue signals, the spike and cosine regressors. LARMORX's port is a replica of
  fMRIPrep 25.2.7's confounds workflow, nipype 1.12.0's confounds module and niworkflows 1.15.4's
  steps, with the arithmetic of numpy, SciPy, pandas, nitime and nipy under them. In `reproduce`
  it gives the originals' outputs bit for bit in each of the 88 cases of its five records, and run
  as fMRIPrep ran it, it writes fMRIPrep's own confounds files of 36 runs column by column. Its
  default, `fix`, corrects the originals' defects or refuses them with a clear error, each with
  the original's result on request.
description: >-
  How LARMORX's replica of fMRIPrep's confound estimation (CompCor, DVARS, framewise displacement,
  the motion parameters, the tissue signals, the confounds table and its JSON) compares with
  fMRIPrep 25.2.7, nipype 1.12.0, niworkflows 1.15.4, numpy, SciPy and pandas, and with fMRIPrep
  25.2.6's own files of 36 runs: four runs' masks and time series, the masks' Gaussian resampling
  and why its last bits differ, every column of every file, the corrections, random testing,
  every case of the records with its verdict, speed and memory.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crate <code>larmorx-confounds</code>; <code>lx.confounds</code>, <code>lx.niworkflows</code>, <code>larmorx nipype run</code> and larmorprepx's confounds workflow, translated from fMRIPrep 25.2.7, nipype 1.12.0 and niworkflows 1.15.4 (fMRIPrep 25.2.6's own releases on request); from the next release
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/confounds-fmriprep.md') }}">fMRIPrep's and niworkflows' steps and the workflow</a> · <a href="{{ repo('docs/validation/confounds-nipype.md') }}">nipype's confounds module and command line</a>, with its <a href="{{ repo('docs/validation/confounds-nipype-full.md') }}">full comparison</a> · <a href="{{ repo('docs/validation/confounds-linalg.md') }}">numpy's and SciPy's linear algebra and FFTs</a>, with its <a href="{{ repo('docs/validation/confounds-linalg-full.md') }}">full comparison</a></dd>
<dt>Reference</dt><dd>API pages <a href="{{ repo('docs/api/confounds.md') }}">confounds</a>, <a href="{{ repo('docs/api/nipype-run.md') }}">nipype-run</a>, <a href="{{ repo('docs/api/niworkflows-helpers.md') }}">niworkflows-helpers</a></dd>
</dl>

## What is compared {#what-it-is}

After head-motion correction, fMRIPrep estimates, for every BOLD run, the time series that a later analysis may regress out: the confounds. Its `init_bold_confs_wf` (fMRIPrep 25.2.7) computes them with nipype's and niworkflows' interfaces and writes them as one table with a JSON that describes each column:

- **The motion parameters** from the head-motion matrices (FSL's convention), their derivatives and squares, the root mean square deviation, and **framewise displacement** (nipype's `FramewiseDisplacement`);
- **DVARS**, raw, standardised and voxel-wise (nipype's `ComputeDVARS`);
- **CompCor**: the anatomical components of the white matter, the CSF and both (aCompCor, on masks resampled from the anatomical tissue maps with a Gaussian kernel), the temporal components of the most variable voxels (tCompCor) and the components of the brain's edge (crownCompCor), with the cosine regressors of the high-pass filter;
- **the tissue signals**: the global, white-matter and CSF means, and their expansion;
- **the outlier regressors**: one column per volume whose framewise displacement or standardised DVARS passes its threshold.

The replica runs beside the originals, run in-process: nipype 1.12.0, niworkflows 1.15.4 and fMRIPrep 25.2.7's interfaces with numpy, SciPy, pandas and nitime. fMRIPrep's own files are those of its runs, with fMRIPrep 25.2.6 and its image's releases (numpy 2.2.6, SciPy 1.15.2, pandas 2.2.3).

```bash
larmorx nipype run nipype.algorithms.confounds ComputeDVARS bold.nii.gz brainmask.nii.gz --save_all
```

```python
import larmorx as lx

# nipype's DVARS: standardised, raw and voxel-wise
dvars = lx.confounds.compute_dvars("bold.nii.gz", "brainmask.nii.gz", n_threads=8)
# nipype's framewise displacement from FSL's motion parameters
fd = lx.confounds.framewise_displacement("motion_params.txt", "FSL", out_dir="work")
```

The [API pages](repo:docs/api/confounds.md) describe every function and option, and larmorprepx's whole confounds workflow of a BOLD run (`bold_confounds`). How to read what follows: [how to read the evidence](/validation/#reading).

### Its port {#ports}

fMRIPrep, nipype, niworkflows, numpy, SciPy, pandas, nitime and nipy are permissive (Apache-2.0, BSD-3-Clause), so the replica is in `larmorx` itself. Their Python is the specification, with the arithmetic of the library releases they call.

- The workflow is a plain Python function (`larmorx.pipelines.larmorprepx.confounds.bold_confounds`), with no nipype and no graph engine. Each node writes its files into the folder nipype would give it, so a run can be compared with fMRIPrep's node folders file by file.
- The numeric routines run in Rust (`larmorx-confounds`): numpy's and SciPy's linear algebra (OpenBLAS' kernels, LAPACK's SVD and least-squares paths), SciPy's FFTs, numpy's reductions and percentiles, and pandas' reading and writing of tables, each in the order of the original's code, so `n_threads` never changes a bit.
- The programs underneath run through LARMORX's own replicas: ANTs' `antsApplyTransforms` for the masks' resampling (`lx.ants`).
- nipype's own command line for these interfaces, `nipypecli run`, is `larmorx nipype run`.

A clean room of these steps is planned after FreeSurfer ([roadmap](/roadmap/)).

## The verdicts at a glance {#verdicts}

The replica is a translation of the originals' source, so the question is whether it gives their bytes.

{{ ev.agreement('confounds', 'port') }}

The records run the originals in-process as the reference, in three Python environments:

- the newest library releases (numpy 2.5.4 with OpenBLAS 0.3.34, SciPy 1.18.1, pandas 3.0.6), LARMORX's reference;
- the releases the other comparisons share (numpy 2.3.5, SciPy 1.15.3);
- fMRIPrep 25.2.6's image (numpy 2.2.6, SciPy 1.15.2, pandas 2.2.3).

They compare the replica with them in `reproduce` (`upstream_defects="reproduce"`): every array, file, table cell, header, warning, message and exit status, bit for bit. The 88 cases of the five records pass, with 4,181 checks. Each case is one of the comparison's check scripts (or one of its sections) run as a process of its own, one check per line it prints.

{{ ev.table('confounds', 'records') }}

## fMRIPrep's own confounds files {#files}

The replica's workflow ran each of the 36 confounds workflows of fMRIPrep 25.2.6's runs end to end, from the workflow's own inputs, as fMRIPrep ran it (`reproduce`, fMRIPrep 25.2.6's releases). Each `desc-confounds_timeseries.tsv` is compared with fMRIPrep's file cell by cell as text, the columns matched by name: their order is that of niworkflows' set, which changes from one process to the next (PIPE-43), so it is never reproduced. Each JSON is compared byte for byte.

The only cells that differ are in the motion chain, where SciPy's rotation calls the C library's `atan2` and the replica computes a correctly rounded one (decision D4: the C library's code is not translated). Run again with fMRIPrep's own motion table, every cell is fMRIPrep's. The table also gives what the newest releases change (the originals' own step, no verdict) and what `fix` changes.

{{ ev.table('confounds', 'files') }}

{{ ev.table('confounds', 'families') }}

{{ ev.table('confounds', 'nodes') }}

## Four runs of fMRIPrep {#examples}

Each example shows one confounds workflow of fMRIPrep's runs: the CompCor masks over the BOLD reference (fMRIPrep's files, the replica in `reproduce` and in `fix`), the confounds' time series, and every column of its table with its verdict. The mask shown is chosen above the viewer.

### ds000005: an adult, 3 T, single-band {#ds000005}

{{ ev.example('confounds', 'confounds-ds000005') }}

### ds000256: a child's run with strong head motion {#ds000256}

{{ ev.example('confounds', 'confounds-ds000256') }}

### ds004958: multiband 8, 600 volumes {#ds004958}

{{ ev.example('confounds', 'confounds-ds004958') }}

### ds003592: an older adult's multi-echo run {#ds003592}

{{ ev.example('confounds', 'confounds-ds003592') }}

## The masks' Gaussian resampling {#gaussian}

fMRIPrep resamples the anatomical tissue maps onto the BOLD grid with ANTs' `antsApplyTransforms -n Gaussian` before it thresholds them into the aCompCor masks. The Gaussian kernel's error function goes through the C library's `exp` and `log` in fMRIPrep's ANTs, and through correctly rounded ones in LARMORX's replica of ANTs. So the resampled probabilities differ in their last bits, and the example traces the cause: ANTs 2.6.5 run with correctly rounded maths gives the replica's bytes, and run as built gives fMRIPrep's. No voxel crosses the masks' thresholds (0.5 and 0.99), so the masks aCompCor reads are fMRIPrep's.

{{ ev.example('confounds', 'confounds-gaussian-ds000005') }}

{{ ev.table('confounds', 'gaussian-runs') }}

## Corrections by default {#corrections}

Every defect the replica found in the originals was decided by the register's rules (A: corrected by default; B: refused with a clear error; C: kept and documented; D: measured first). `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release) gives the original's behaviour, its errors and warnings included.

- 49 entries were registered: PIPE-41 to PIPE-83 in nipype, niworkflows and fMRIPrep, PD-01 to PD-03 in pandas, NP-09 and NP-10 in numpy, SCI-41 in SciPy.
- 29 are corrected by default (two undefined conversions clamped) and 12 refused with a clear error, 41 with the switch; among them every confounds JSON's missing tissue-signal entries (PIPE-41) and nipype's file names with a blank.
- GLIBC-07, the C library's cosine: in `fix` the cosine regressors take the correctly rounded `cos`, which turns the sign of some CompCor components (the multi-echo example above).

{{ ev.table('confounds', 'corrections') }}

## Speed {#speed}

The benchmark ([report](repo:docs/benchmarks/confounds.md)) runs fMRIPrep's nodes in-process on their own inputs of three fMRIPrep runs, and the replica on the same inputs, every result checked byte for byte.

- The 26 Python nodes run 1.1 to 1.4 times as fast as fMRIPrep's at one thread, and 1.5 to 1.6 times at eight.
- numpy's SVD and least squares, ported in Rust, are still slower than numpy's own (their kernels without FMA dispatch): a speed item for later.

{{ ev.speed('confounds') }}

## Memory {#memory}

The memory rule allows LARMORX at most 10 % above the original's peak plus 8 MiB for the same call; here the replica needs at most 0.96 of the originals' peak.

{{ ev.table('confounds', 'memory') }}

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the originals and the replica and compares every output ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a permanent case, registered as a defect of the original, or reported. The replica's run of 2026-11-12 (30 minutes) and two checks of the final build compared 514,694 random calls.

{{ ev.table('confounds', 'trial') }}

{{ ev.table('confounds', 'triage') }}

## Every case {#cases}

Each case of the records, with what it tests, its command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('confounds') }}

## Known limits {#limits}

- fMRIPrep's confounds with FreeSurfer's segmentation (its runs with `recon-all`) are not compared yet: PIPE-79 waits for fMRIPrep's runs with FreeSurfer.
- fMRIPrep's reports of the confounds (its reportlets) come with larmorprepx's reports.
- The comparisons with fMRIPrep stage by stage come once every program is ported.

## History {#history}

- **2026-11-12**: the replica's random-testing run and the checks of the final build.
- **2026-11-13**: the replica of fMRIPrep's confound estimation complete, with nipype's command line and numpy's and SciPy's linear algebra ([the roadmap](/roadmap/#done)).
