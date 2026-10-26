---
title: 3dUnifize
kicker: Tools · AFNI
lede: >-
  AFNI's white-matter uniformization of a T1w (or, with -T2, a T2w or an EPI image), in two
  implementations: an exact replica of AFNI's source in the separate larmorx-gpl package,
  bit-identical to AFNI 25.2.09 in every compared case, and a clean-room original in LARMORX
  (Apache-2.0), written from a behavioural specification, whose outputs are AFNI's bytes with
  correctly rounded maths, fMRIPrep's own calls included.
description: LARMORX's two implementations of AFNI's 3dUnifize, validated against AFNI 25.2.09 and fMRIPrep 25.2.6 — fMRIPrep's uniformization of a real BOLD reference, a real T1w and a deliberate correction to inspect, AFNI at 1 and 6 threads and with correctly rounded maths, and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-gpl</code>, GPL-3.0-or-later, run as a separate program); clean-room original (<code>larmorx</code>, Apache-2.0, from <a href="{{ repo('specs/3dUnifize.md') }}">specs/3dUnifize.md</a>)</dd>
<dt>Status</dt><dd><span class="status-tag eco-afni">validated</span> (each)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/afni-unifize-replica.md') }}">replica</a> · <a href="{{ repo('docs/validation/afni-unifize.md') }}">original</a> · API <a href="{{ repo('docs/api/afni-unifize.md') }}">afni-unifize</a></dd>
</dl>

## What it is

3dUnifize divides each voxel by the local white-matter level, a mean of the upper percentiles of the masked values in a ball around it (`-Urad`, 18.3 voxels across by default, whatever the voxel size; on a half-size copy above a million voxels), scales white matter to 1000 and squashes the brightest values. With `-T2` it inverts the contrast first and back after; `-GM` also scales grey matter; `-EPI` works volume by volume. fMRIPrep calls it once per BOLD run, with `-T2`, on its skull-stripped BOLD reference, before the second skull strip ([3dAutomask](/tools/afni-automask/)).

```bash
larmorx afni 3dUnifize -clfrac 0.2 -rbt 18.3 65.0 90.0 -prefix uni.nii.gz -T2 -input ref_brain.nii.gz
```

```python
import larmorx as lx

uni = lx.afni.unifize("ref_brain.nii.gz", **lx.afni.fmriprep_unifize_options(), n_threads=6)
t1 = lx.afni.unifize("sub-01_T1w.nii.gz", save_scale=True)   # implementation="auto"
```

3dUnifize's results depend on AFNI library routines copyrighted by the Medical College of Wisconsin (GPL-2), so LARMORX has two implementations. `implementation="auto" | "replica" | "original"` chooses (on the command line `LARMORX_IMPLEMENTATION`); `auto` takes the replica when `larmorx-gpl` is installed (`pip install "larmorx[exact]"`), and the clean-room original otherwise. The squash calls `tanhf`: the replica carries a port of glibc 2.35's, checked against glibc on all 2<sup>32</sup> float inputs; the original uses a correctly rounded one (a port of CORE-MATH's), as every LARMORX function does. The original's ball percentiles are its speed: instead of gathering and sorting some 25,000 values at every voxel, it slides a window of counts per rank from voxel to voxel, changing only the ball's two surfaces, and reads the values between the two percentiles in ascending order, which gives the specification's sum exactly; planes run in parallel, with the same bytes at any thread count. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('afni-unifize', 'replica') }}

{{ ev.agreement('afni-unifize', 'original') }}

Both records run the same 99 cases against AFNI 25.2.09, with AFNI's exit status and messages in every case. The replica gives AFNI's bytes in every case that writes an output. The clean-room original gives them in 34 of the 74 compared cases that write outputs; in the other 40 its headers are AFNI's and a few squashed values (above 1300) differ in their last bit, at most 1,633 values of a T1w and 8.7 × 10<sup>−8</sup> of the largest value, against a threshold of 10<sup>−5</sup>: AFNI's squash calls glibc's `tanhf`, which is not correctly rounded on some arguments, the original's is. Run with CORE-MATH's correctly rounded functions preloaded, AFNI gives the original's bytes in all 40 (*identical with correctly rounded maths*). AFNI computes every voxel's local level independently in its OpenMP loop: its result does not depend on the thread count, and neither does either implementation's. Where AFNI crashes (AFNI-40, AFNI-46), both stop with an error instead; where AFNI reads past the end of its half-size scale image (AFNI-47, a volume of more than a million voxels only two slices thick), AFNI crashed in our runs and both define the result.

## In fMRIPrep: a BOLD reference {#example}

fMRIPrep's own call on one of its oracle runs, given to AFNI at one and six OpenMP threads, to the replica at one and six threads in both modes, beside the output fMRIPrep produced in its run; then to the clean-room original at one and six threads and in both modes, and to AFNI with CORE-MATH's correctly rounded functions preloaded.

{{ ev.example('afni-unifize', 'fmriprep-unifize') }}

## A T1w, on the half-size path {#t1w}

Above a million voxels, 3dUnifize computes the local white-matter level on a half-size copy and brings it back; choose *Scale image* above the panels for the factor each voxel is multiplied by.

{{ ev.example('afni-unifize', 't1w-unifize') }}

## A deliberate correction: AFNI-45 {#correction}

At `-T2up 100`, the upper percentile 3dUnifize inverts about is read one past the end of the sorted values ([AFNI-45](repo:docs/findings/upstream-defects.md)): what AFNI finds there is memory it never wrote. Both implementations' default inverts about the largest value, and warns; `reproduce` fills the read with 0, as AFNI read it here.

{{ ev.example('afni-unifize', 'afni-45') }}

## Every case {#cases}

Each case of the two records, with what it tests, its command line, the verdict of each implementation and the reason. Search, filter (or select a segment of a chart above), sort; `#case=<name>` links to one.

{{ ev.cases('afni-unifize') }}

## Speed {#speed}

{{ ev.speed('afni-unifize') }}

The clean-room original is 4 to 25 times faster than AFNI at the same thread count, and 3 to 10 times faster than the replica, which computes as AFNI does: its ball percentiles slide from voxel to voxel instead of being gathered and sorted at every voxel. On the half-size path the ball works on an eighth of the voxels, and reading and writing the full-size compressed images takes a larger share of the time. These are informal timings on a shared machine ([findings](repo:docs/findings/afni-masks-original.md)); there is no benchmark report yet.

## Corrections by default {#corrections}

Both implementations correct AFNI's deterministic defects by default and warn: the records' fix passes meet AFNI-45 (`-T2up` near 100), AFNI-47 (a volume of more than a million voxels with an axis of 2 or 3), AFNI-01 (`-EPI`'s median of a series with a negative scale factor) and the dataset defects 3dUnifize shares with 3dTshift (AFNI-02, AFNI-07, AFNI-11, AFNI-12, AFNI-16, AFNI-18, AFNI-23, AFNI-26), with `upstream_defects="reproduce"` giving AFNI's behaviour ([register](repo:docs/findings/upstream-defects.md)). AFNI-48 (`-T2` given three times without `-EPI`, which leaves the output inverted) is refused by default, in the same words by both implementations (decided 2026-10-23), with `reproduce` giving AFNI's output.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, a night at a time: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest night:

{{ ev.random_testing('/tools/afni-unifize/') }}

## Known limits {#limits}

LARMORX writes NIfTI only: AFNI's default prefix `Unifized` is its own dataset format, which both implementations refuse (an expected divergence). The original's squashed values (above 1300) can differ from AFNI's in their last bit where glibc's `tanhf` is not correctly rounded; AFNI with correctly rounded maths gives the original's bytes. There is no benchmark report yet. The golden tests cannot reach the half-size path (more than a million voxels, beyond their 32³ budget); the parity records cover it on real T1w images. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md).
