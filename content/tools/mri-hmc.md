---
title: Head-motion correction
kicker: Tools · FSL-compatible
lede: >-
  Rigid head-motion correction of BOLD runs with mcflirt's options, a clean-room original in
  LARMORX (Apache-2.0). Experimental: one of its 122 compared cases misses its threshold.
description: LARMORX's clean-room head-motion correction with mcflirt-style options, its validation against FSL 6.0.7's mcflirt in figures, motion traces on a real run against mcflirt's own variability, and speed.
---

<dl class="facts">
<dt>Implementation</dt><dd>clean-room original (<code>larmorx</code>, Apache-2.0), written from <a href="{{ repo('specs/mcflirt.md') }}">specs/mcflirt.md</a> and black-box runs of mcflirt; the exact replica (<code>larmorx-nc</code>) is not started</dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/mri-hmc.md') }}">mri-hmc</a> · benchmark <a href="{{ repo('docs/benchmarks/mri-hmc.md') }}">mri-hmc</a> · API <a href="{{ repo('docs/api/mri-hmc.md') }}">mri-hmc</a></dd>
</dl>

## What it is

Head-motion correction estimates, for every volume of a BOLD run, the rigid transform that aligns it to a reference volume, in mcflirt's coarse-to-fine schedule, and optionally resamples the run. fMRIPrep runs mcflirt with its BOLD reference and keeps the matrices.

## How to call it

```bash
larmorx mri hmc -in bold.nii.gz -out bold_mcf.nii.gz -reffile hmc_boldref.nii.gz -mats -plots
```

```python
import larmorx as lx

hmc = lx.mri.hmc("sub-01_task-rest_bold.nii.gz", reference="hmc_boldref.nii.gz",
                 resample=False, n_threads=8)
hmc.matrices          # (N, 4, 4) FSL matrices, as mcflirt's MAT_* files
hmc.save_itk("mat2itk.txt")
```

## Agreement with mcflirt

A clean-room original is not expected to give mcflirt's bits; the [record](repo:docs/validation/mri-hmc.md) holds it to thresholds on the motion estimates, or to mcflirt's own variability where that is wider: mcflirt's result when its input is perturbed slightly (noise of ±0.5 and the volumes in reverse order). Of 134 cases, 121 pass, 11 are rejected by both, 1 is an expected divergence and 1 fails (`real/ds003345/default`, mcflirt's defaults with the middle volume as reference). Over the 116 runs with matrices, the worst 95th-percentile RMS deviation from mcflirt is 0.28 mm (25 runs use mcflirt's band); against the synthetic series' true motion, LARMORX's mean RMS deviation is 0.409 mm and mcflirt's 0.414 mm.

{{ figure('mri-hmc/agreement', "The record's 134 cases by category: within the thresholds (or mcflirt's band where wider), the one failure, the expected divergence and the inputs both refuse.") }}

## A real run

{{ figure('mri-hmc/motion', "fMRIPrep's command (`-reffile` with fMRIPrep 21.0.1's published BOLD reference, `-mats -plots`) on OpenNeuro ds000005 sub-01's first BOLD run (PDDL-1.0, 240 volumes): the six motion parameters of every volume from mcflirt (FSL 6.0.7.17, the recorded oracle run) and from LARMORX in the record's comparison mode, and the framewise displacement of both.") }}

{{ figure('mri-hmc/deviation', "The same run: per volume, the RMS deviation (80 mm sphere) of LARMORX's matrices from mcflirt's, in the comparison mode and in LARMORX's default mode, next to mcflirt's own deviation when its input is perturbed slightly (three noise realisations and the reverse order). The default mode differs in the last volume, which it initialises from the previous one (FSL-01).") }}

## Speed

{{ figure('mri-hmc/speed', "Median seconds of fMRIPrep's command (`-reffile -mats`, the corrected series written) for mcflirt (single-threaded) and LARMORX's command line at 1 and 12 threads, on three real runs, from the benchmark report of 2026-10-10 (Intel i7-8750H, 12 logical CPUs; the report notes the machine's load); the factor is LARMORX's speed-up at one thread.") }}

## Corrections by default

The record's fix pass meets FSL-01 (the last volume not initialised from the previous one, every run), FSL-03, FSL-05, FSL-06, FSL-08, FSL-09, FSL-10, FSL-13 and FSL-14; each is corrected by default, with `upstream_defects="reproduce"` giving mcflirt's behaviour, the mode the comparison runs in ([register](repo:docs/findings/upstream-defects.md)). On the 52 real runs, a run's largest change from the corrections is 0.024 mm at the median and 72.1 mm at most.

## Known limits

Experimental until every compared case meets its threshold. The bit-exact replica of mcflirt, in the separately licensed `larmorx-nc` package, is planned.
