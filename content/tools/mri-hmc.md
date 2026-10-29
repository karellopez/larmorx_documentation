---
title: Head-motion correction
kicker: Tools · FSL-compatible
lede: >-
  Rigid head-motion correction of BOLD runs with mcflirt's options, in two implementations: a
  clean-room original in LARMORX (Apache-2.0), experimental: on fMRIPrep's own run its motion
  estimates stay within mcflirt's own variability, and the cases where that variability is not
  measured, or is exceeded, are open; and an exact replica of mcflirt's source in the separate
  larmorx-nc package (FSL Licence, non-commercial), bit-identical to mcflirt in every compared
  case (173 of 173).
description: LARMORX's head-motion correction with mcflirt's options, a clean-room original and a bit-exact replica, validated against FSL 6.0.7's mcflirt — fMRIPrep's mcflirt command on a real run to inspect, the six parameters and FD over the run against mcflirt's perturbation band, the corrections, every parity case of both records with its verdict, and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>clean-room original (<code>larmorx</code>, Apache-2.0), written from <a href="{{ repo('specs/mcflirt.md') }}">specs/mcflirt.md</a> and black-box runs of mcflirt; exact replica (<code>larmorx-nc</code>, the FSL Licence: non-commercial use only, FSL's source included; run as a separate program), translated from FSL 6.0.7.17's source</dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span> (original) · <span class="status-tag eco-fsl">validated</span> (replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/mri-hmc.md') }}">mri-hmc</a> (original) · <a href="{{ repo('docs/validation/fsl-mcflirt-replica.md') }}">fsl-mcflirt-replica</a> (replica) · benchmark <a href="{{ repo('docs/benchmarks/mri-hmc.md') }}">mri-hmc</a> · API <a href="{{ repo('docs/api/mri-hmc.md') }}">mri-hmc</a></dd>
</dl>

## What it is

Head-motion correction estimates, for every volume of a BOLD run, the rigid transform that aligns it to a reference volume, in mcflirt's coarse-to-fine schedule, and optionally resamples the run. fMRIPrep runs mcflirt with its BOLD reference and keeps the matrices.

```bash
larmorx mri hmc -in bold.nii.gz -out bold_mcf.nii.gz -reffile hmc_boldref.nii.gz -mats -plots
larmorx fsl mcflirt -in bold.nii.gz -out bold_mcf.nii.gz -reffile hmc_boldref.nii.gz -mats -plots   # the replica, if installed
```

```python
import larmorx as lx

hmc = lx.mri.hmc("sub-01_task-rest_bold.nii.gz", reference="hmc_boldref.nii.gz",
                 resample=False, n_threads=8)
hmc.matrices          # (N, 4, 4) FSL matrices, as mcflirt's MAT_* files
hmc.implementation    # which implementation ran
```

`implementation="auto" | "replica" | "original"` chooses (on the command line `LARMORX_IMPLEMENTATION`); `auto` takes the replica when `larmorx-nc` is installed (`pip install larmorx-nc`, by name, so that its non-commercial licence is accepted knowingly).

How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

A clean-room original is written without mcflirt's source, so it is not expected to give mcflirt's bits; the question is whether its estimates differ from mcflirt's by no more than mcflirt's own differ when its input changes imperceptibly. mcflirt is deterministic, so that variability is measured by perturbing its input: noise of half a quantisation step (three realisations) and the volumes in reverse order ([the record](repo:docs/validation/mri-hmc.md)). A case is *within the original's variability* when every compared estimate is inside that band; it is *open* when it exceeds the band, or when the band is not measured for that case (the options and synthetic series), even though it meets the record's thresholds.

{{ ev.agreement('mri-hmc', 'original') }}

The replica is a translation of mcflirt's own source, so the question for it is whether it gives mcflirt's bytes: every output file, the exit status and both message streams, compared with mcflirt as built (FSL 6.0.7.17, with the C library's maths it calls on Linux). Its record runs the 137 recorded mcflirt runs above, fMRIPrep's own mcflirt calls on the twelve oracle runs that have BOLD runs (22 calls, the data panel's included: a child's extreme motion, 1.5 T, multiband-8 with 600 volumes, multi-echo, a stroke, a glioma; fMRIPrep's 4,517 matrices identical too), and edge cases made for it (the failure cases, every output type, `-gdt`, `-verbose 20`, histogram costs with few bins, moving phantoms) ([the record](repo:docs/validation/fsl-mcflirt-replica.md)). Two of the panel's calls and 58 of the first 59 differences random testing found came from one constant of the C library's `atanf` in the replica's translation: `aT[0]` had been taken from fdlibm's source comment (`0x3eaaaaaa`) instead of its decimal value (`0x3eaaaaab`, the value glibc holds), which moved one rotation angle by one ulp (on ds002422's rest run, in 1 of mcflirt's 600 rotation decompositions); with it corrected, every one of them is bit-identical, and the last one was a missing FSL-08 notice, now given ([findings](repo:docs/findings/fsl-mcflirt.md)).

{{ ev.agreement('mri-hmc', 'replica') }}

## A worked example: fMRIPrep's mcflirt {#example}

fMRIPrep's own call on OpenNeuro ds000005's first run: its command, its BOLD and its HMC reference, given to FSL 6.0.7's mcflirt and to LARMORX's two implementations. The chart under the viewer has the six parameters and the framewise displacement of every volume, and each implementation's deviation from mcflirt's matrix next to mcflirt's own band: the replica's is zero at every volume.

{{ ev.example('mri-hmc', 'fmriprep-hmc') }}

## Every case {#cases}

Each case of the two records, with what it tests, the command line, the verdict of each implementation and the reason; the replica's edge cases and fMRIPrep's calls are cases of their own. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('mri-hmc') }}

## Speed {#speed}

{{ ev.speed('mri-hmc') }}

## Corrections by default {#corrections}

The record's fix pass meets FSL-01 (the last volume not initialised from the previous one), FSL-03, FSL-05, FSL-06, FSL-08, FSL-09, FSL-10, FSL-13 and FSL-14; each is corrected by default, with `upstream_defects="reproduce"` giving mcflirt's behaviour, the mode the comparison runs in ([register](repo:docs/findings/upstream-defects.md)). The worked example shows what they change on fMRIPrep's run.

The replica corrects the same defects the same way by default, and three more that its translation found: `-gdt` (FSL-04: refused; `reproduce` registers the gradient images as mcflirt does), a `.mat` directory that cannot be created (FSL-20: mcflirt exits with status 0 having written nothing more; an error), and the histogram costs with fewer than 8 bins (FSL-21: the first stage has no bins, the matrices are arbitrary, and `corratio` corrupts its heap and aborts; refused). `reproduce` gives mcflirt's bytes, aborts included.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/mri-hmc/') }}

## What is open {#open}

{{ ev.table('mri-hmc', 'open') }}

- One case misses its threshold: `real/ds003345/default` (mcflirt's defaults, the middle volume as reference), whose framewise displacement correlates with mcflirt's at r = 0.9885 where mcflirt's own band reaches 0.9893.
- mcflirt's variability is measured for fMRIPrep's command on the nine real runs, for mcflirt's defaults on most of them and for a few synthetic series; the options and the other synthetic series are held to the record's fixed thresholds only, so they stay open until their band is measured.
- The bit-exact replica of mcflirt, in the separately licensed `larmorx-nc` package, is done: 173 of 173 compared cases bit-identical to mcflirt as built, and mcflirt's messages and exit status in the 21 where both fail. For the clean-room original, FSL-20 and FSL-21 are still to be specified and corrected.
