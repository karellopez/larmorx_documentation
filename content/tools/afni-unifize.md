---
title: 3dUnifize
kicker: Tools · AFNI
lede: >-
  AFNI's white-matter uniformization of a T1w (or, with -T2, a T2w or an EPI image), as an
  exact replica of AFNI's source in the separate larmorx-gpl package: bit-identical to AFNI
  25.2.09 in every compared case, at any thread count, fMRIPrep's own calls included. A
  clean-room original in LARMORX (Apache-2.0) is still to be written from its specification.
description: LARMORX's replica of AFNI's 3dUnifize, validated against AFNI 25.2.09 and fMRIPrep 25.2.6 — fMRIPrep's uniformization of a real BOLD reference, a real T1w and a deliberate correction to inspect, AFNI at 1 and 6 threads, and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-gpl</code>, GPL-3.0-or-later, run as a separate program); clean-room original: not yet, to be written from <a href="{{ repo('specs/3dUnifize.md') }}">specs/3dUnifize.md</a></dd>
<dt>Status</dt><dd><span class="status-tag eco-afni">validated</span> (the replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/afni-unifize.md') }}">afni-unifize</a> · API <a href="{{ repo('docs/api/afni-unifize.md') }}">afni-unifize</a></dd>
</dl>

## What it is

3dUnifize divides each voxel by the local white-matter level, a mean of the upper percentiles of the masked values in a ball around it (`-Urad`, 18.3 voxels across by default, whatever the voxel size; on a half-size copy above a million voxels), scales white matter to 1000 and squashes the brightest values. With `-T2` it inverts the contrast first and back after; `-GM` also scales grey matter; `-EPI` works volume by volume. fMRIPrep calls it once per BOLD run, with `-T2`, on its skull-stripped BOLD reference, before the second skull strip ([3dAutomask](/tools/afni-automask/)).

```bash
larmorx afni 3dUnifize -clfrac 0.2 -rbt 18.3 65.0 90.0 -prefix uni.nii.gz -T2 -input ref_brain.nii.gz
```

```python
import larmorx as lx

uni = lx.afni.unifize("ref_brain.nii.gz", **lx.afni.fmriprep_unifize_options(), n_threads=6)
t1 = lx.afni.unifize("sub-01_T1w.nii.gz", save_scale=True)
```

3dUnifize's results depend on AFNI library routines copyrighted by the Medical College of Wisconsin (GPL-2), so the replica lives in `larmorx-gpl` (`pip install "larmorx[exact]"`), which LARMORX runs as a separate program. Its squash calls the C library's `tanhf`: the replica carries a port of glibc 2.35's, checked against glibc on all 2<sup>32</sup> float inputs. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('afni-unifize', 'replica') }}

The replica gives AFNI's bytes in every case that writes an output, and AFNI's exit status and messages in every case. AFNI computes every voxel's local level independently in its OpenMP loop: its result does not depend on the thread count, and neither does the replica's. Where AFNI crashes (AFNI-40, AFNI-46), the replica stops with an error instead; where AFNI reads past the end of its half-size scale image (AFNI-47, a volume of more than a million voxels only two slices thick), AFNI crashed in our runs and the replica defines the result.

## In fMRIPrep: a BOLD reference {#example}

fMRIPrep's own call on one of its oracle runs, given to AFNI at one and six OpenMP threads and to the replica at one and six threads in both modes, beside the output fMRIPrep produced in its run.

{{ ev.example('afni-unifize', 'fmriprep-unifize') }}

## A T1w, on the half-size path {#t1w}

Above a million voxels, 3dUnifize computes the local white-matter level on a half-size copy and brings it back; choose *Scale image* above the panels for the factor each voxel is multiplied by.

{{ ev.example('afni-unifize', 't1w-unifize') }}

## A deliberate correction: AFNI-45 {#correction}

At `-T2up 100`, the upper percentile 3dUnifize inverts about is read one past the end of the sorted values ([AFNI-45](repo:docs/findings/upstream-defects.md)): what AFNI finds there is memory it never wrote. The replica's default inverts about the largest value, and warns; `reproduce` fills the read with 0, as AFNI read it here.

{{ ev.example('afni-unifize', 'afni-45') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, the verdict and the reason. Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('afni-unifize') }}

## Corrections by default {#corrections}

The replica corrects AFNI's deterministic defects by default and warns: the record's fix pass meets AFNI-45 (`-T2up` near 100), AFNI-47 (a volume of more than a million voxels with an axis of 2 or 3), AFNI-01 (`-EPI`'s median of a series with a negative scale factor) and the dataset defects 3dUnifize shares with 3dTshift (AFNI-02, AFNI-07, AFNI-11, AFNI-12, AFNI-16, AFNI-18, AFNI-23, AFNI-26), with `upstream_defects="reproduce"` giving AFNI's behaviour ([register](repo:docs/findings/upstream-defects.md)). AFNI-48 (`-T2` given three times) behaves as in AFNI until it is decided.

## Known limits {#limits}

LARMORX writes NIfTI only: AFNI's default prefix `Unifized` is its own dataset format, which the replica refuses (an expected divergence). There is no clean-room original yet, so `implementation="original"` is an error. There is no benchmark report. The golden tests cannot reach the half-size path (more than a million voxels, beyond their 32³ budget); the parity record covers it on real T1w images. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md).
