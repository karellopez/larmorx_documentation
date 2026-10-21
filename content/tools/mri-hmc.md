---
title: Head-motion correction
kicker: Tools · FSL-compatible
lede: >-
  Rigid head-motion correction of BOLD runs with mcflirt's options, a clean-room original in
  LARMORX (Apache-2.0). Experimental: on fMRIPrep's own run its motion estimates stay within
  mcflirt's own variability; across the record, the cases where mcflirt's variability is not
  measured, or is exceeded, are open.
description: LARMORX's clean-room head-motion correction with mcflirt-style options, validated against FSL 6.0.7's mcflirt — fMRIPrep's mcflirt command on a real run to inspect, the six parameters and FD over the run against mcflirt's perturbation band, the corrections, every parity case with its verdict, and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>clean-room original (<code>larmorx</code>, Apache-2.0), written from <a href="{{ repo('specs/mcflirt.md') }}">specs/mcflirt.md</a> and black-box runs of mcflirt; the exact replica (<code>larmorx-nc</code>) is not started</dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/mri-hmc.md') }}">mri-hmc</a> · benchmark <a href="{{ repo('docs/benchmarks/mri-hmc.md') }}">mri-hmc</a> · API <a href="{{ repo('docs/api/mri-hmc.md') }}">mri-hmc</a></dd>
</dl>

## What it is

Head-motion correction estimates, for every volume of a BOLD run, the rigid transform that aligns it to a reference volume, in mcflirt's coarse-to-fine schedule, and optionally resamples the run. fMRIPrep runs mcflirt with its BOLD reference and keeps the matrices.

```bash
larmorx mri hmc -in bold.nii.gz -out bold_mcf.nii.gz -reffile hmc_boldref.nii.gz -mats -plots
```

```python
import larmorx as lx

hmc = lx.mri.hmc("sub-01_task-rest_bold.nii.gz", reference="hmc_boldref.nii.gz",
                 resample=False, n_threads=8)
hmc.matrices          # (N, 4, 4) FSL matrices, as mcflirt's MAT_* files
```

How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

A clean-room original is written without mcflirt's source, so it is not expected to give mcflirt's bits; the question is whether its estimates differ from mcflirt's by no more than mcflirt's own differ when its input changes imperceptibly. mcflirt is deterministic, so that variability is measured by perturbing its input: noise of half a quantisation step (three realisations) and the volumes in reverse order ([the record](repo:docs/validation/mri-hmc.md)). A case is *within the original's variability* when every compared estimate is inside that band; it is *open* when it exceeds the band, or when the band is not measured for that case (the options and synthetic series), even though it meets the record's thresholds.

{{ ev.agreement('mri-hmc', 'original') }}

## A worked example: fMRIPrep's mcflirt {#example}

fMRIPrep's own call on OpenNeuro ds000005's first run: its command, its BOLD and its HMC reference, given to FSL 6.0.7's mcflirt and to LARMORX. The chart under the viewer has the six parameters and the framewise displacement of every volume, and LARMORX's deviation from mcflirt's matrix next to mcflirt's own band.

{{ ev.example('mri-hmc', 'fmriprep-hmc') }}

## Every case {#cases}

Each case of the record, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('mri-hmc') }}

## Speed {#speed}

{{ ev.speed('mri-hmc') }}

## Corrections by default {#corrections}

The record's fix pass meets FSL-01 (the last volume not initialised from the previous one), FSL-03, FSL-05, FSL-06, FSL-08, FSL-09, FSL-10, FSL-13 and FSL-14; each is corrected by default, with `upstream_defects="reproduce"` giving mcflirt's behaviour, the mode the comparison runs in ([register](repo:docs/findings/upstream-defects.md)). The worked example shows what they change on fMRIPrep's run.

## What is open {#open}

{{ ev.table('mri-hmc', 'open') }}

- One case misses its threshold: `real/ds003345/default` (mcflirt's defaults, the middle volume as reference), whose framewise displacement correlates with mcflirt's at r = 0.9885 where mcflirt's own band reaches 0.9893.
- mcflirt's variability is measured for fMRIPrep's command on the nine real runs, for mcflirt's defaults on most of them and for a few synthetic series; the options and the other synthetic series are held to the record's fixed thresholds only, so they stay open until their band is measured.
- The bit-exact replica of mcflirt, in the separately licensed `larmorx-nc` package, is planned.
