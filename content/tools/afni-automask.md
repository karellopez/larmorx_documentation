---
title: 3dAutomask
kicker: Tools · AFNI
lede: >-
  AFNI's brain mask of an EPI series or a skull-stripped image, in two implementations: an
  exact replica of AFNI's source in the separate larmorx-gpl package, and a clean-room original
  in LARMORX (Apache-2.0), written from a behavioural specification. Both give AFNI 25.2.09's
  masks bit for bit in every compared case, fMRIPrep's own calls included.
description: LARMORX's two implementations of AFNI's 3dAutomask, validated against AFNI 25.2.09 and fMRIPrep 25.2.6 — fMRIPrep's skull strip of a real BOLD reference, a raw BOLD series and a deliberate correction to inspect, and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-gpl</code>, GPL-3.0-or-later, run as a separate program); clean-room original (<code>larmorx</code>, Apache-2.0, from <a href="{{ repo('specs/3dAutomask.md') }}">specs/3dAutomask.md</a>)</dd>
<dt>Status</dt><dd><span class="status-tag eco-afni">validated</span> (each)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/afni-automask-replica.md') }}">replica</a> · <a href="{{ repo('docs/validation/afni-automask.md') }}">original</a> · API <a href="{{ repo('docs/api/afni-automask.md') }}">afni-automask</a></dd>
</dl>

## What it is

3dAutomask makes a brain mask from the intensities alone: it averages the absolute values of a series' volumes, finds a clip level from their histogram (gradually, octant by octant, unless `-nograd`), keeps the largest connected cluster above it, peels and unpeels it to cut off thin protrusions, and fills its holes. fMRIPrep calls it once per BOLD run, on its unifized BOLD reference, with `-dilate 1` and `-apply_prefix`: the second skull strip of its BOLD reference workflow.

```bash
larmorx afni 3dAutomask -apply_prefix uni_xform_masked.nii.gz -dilate 1 -prefix uni_xform_mask.nii.gz uni_xform.nii.gz
```

```python
import larmorx as lx

r = lx.afni.automask("uni_xform.nii.gz", dilate=1, apply=True)   # implementation="auto"
r.mask, r.masked
```

3dAutomask's results depend on AFNI library routines copyrighted by the Medical College of Wisconsin (GPL-2), so LARMORX has two implementations. `implementation="auto" | "replica" | "original"` chooses (on the command line `LARMORX_IMPLEMENTATION`); `auto` takes the replica when `larmorx-gpl` is installed (`pip install "larmorx[exact]"`), and the clean-room original otherwise. The original decides each pass of its mask operations voxel by voxel in parallel, finds clusters by union-find over runs of voxels and replaces two of AFNI's repeated sweeps by breadth-first searches with the same result; its result does not depend on the thread count. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('afni-automask', 'replica') }}

{{ ev.agreement('afni-automask', 'original') }}

Both records run the same 109 cases against AFNI 25.2.09. The replica gives AFNI's bytes, data and NIfTI header, in every case that writes an output, and AFNI's exit status and messages in every case. So does the clean-room original, but in one case: fMRIPrep's call on the BOLD reference of ds005454, whose header differs where AFNI reads the input's geometry from its own header extension, in 7 significant digits (AFNI-10, the *deliberate correction*); its masks are AFNI's. Where AFNI crashes on a missing option value (AFNI-40), both stop with an error instead: the expected divergences. Each case is also run in the default mode, where LARMORX corrects AFNI's deterministic defects and names them.

## In fMRIPrep: the BOLD reference's second skull strip {#example}

fMRIPrep's own call on one of its oracle runs, given to AFNI, to fMRIPrep's build of AFNI, to the replica and to the clean-room original (at 1 and 6 threads). Each mask is drawn over the image it was made from; choose *Masked input* above the panels for `-apply_prefix`'s output, and the difference panels for what separates two runs.

{{ ev.example('afni-automask', 'fmriprep-automask') }}

## A raw BOLD series {#bold}

The functional path: with several volumes, 3dAutomask first averages their absolute values, then masks the average.

{{ ev.example('afni-automask', 'bold-automask') }}

## A deliberate correction: AFNI-43 {#correction}

3dAutomask's help says `-peels 0` turns the peeling off; AFNI peels once instead ([AFNI-43](repo:docs/findings/upstream-defects.md)). Both implementations' default does not peel, and warns; `reproduce` gives AFNI's mask.

{{ ev.example('afni-automask', 'afni-43') }}

## On the data panel: extreme head motion {#panel}

The first case of the [data panel](/data-panel/) on this page, added beside the examples above: AFNI's default on a child's resting-state run with extreme head motion (OpenNeuro ds000256), the whole field of view shown, its noise and the masks' edges included. Like every panel case that is not one of a tool's key datasets, it is stored as three full-resolution slices through the voxel where the comparison differs most (the field's centre where nothing differs); its metrics are over every voxel.

{{ ev.example('afni-automask', 'panel-ds000256-motion') }}

## Every case {#cases}

Each case of the two records, with what it tests, its command line, the verdict of each implementation and the reason. Search, filter (or select a segment of a chart above), sort; `#case=<name>` links to one.

{{ ev.cases('afni-automask') }}

## Speed {#speed}

{{ ev.speed('afni-automask') }}

3dAutomask is quick in every implementation: its time is mostly reading and writing compressed NIfTI, and AFNI's is single-threaded. These are informal timings on a shared machine ([findings](repo:docs/findings/afni-masks-original.md)); there is no benchmark report yet.

## Corrections by default {#corrections}

Both implementations correct AFNI's deterministic defects by default and warn: the records' fix passes meet AFNI-43 (`-peels 0`), AFNI-01 (a negative scale factor dropped while averaging a series) and the dataset defects 3dAutomask shares with 3dTshift (AFNI-02, AFNI-07, AFNI-11, AFNI-12, AFNI-16, AFNI-18, AFNI-23, AFNI-26), with `upstream_defects="reproduce"` giving AFNI's behaviour ([register](repo:docs/findings/upstream-defects.md)). AFNI-41 (`-nbhrs` outside 6 to 26, silently 17 in AFNI) is refused by default before any input is read, in the same words by both implementations (decided 2026-10-23), with `reproduce` giving AFNI's mask; AFNI-42 (`-NN1/2/3` reset the peel threshold) and AFNI-44 (the large-hole filling decided by the number of slices) are kept as AFNI's and documented.

**Refused by default: AFNI-41.** `-nbhrs` takes a value between 6 and 26, as the help says; outside that range AFNI accepts it silently and peels as with 17. A value outside the range makes no sense, and the project's rule for that case (2026-10-23) is a clear error: by default the replica stops with a message naming AFNI-41, before reading the input; `LARMORX_UPSTREAM_DEFECTS=reproduce` gives AFNI's mask, bit for bit. The case explorer shows it: [options/nbhrs-40](#case=options/nbhrs-40), and in the standard tier `nbhrs-5`, `nbhrs-27`, `nbhrs-0` and `nbhrs-40-then-NN1`, each with the verdict *deliberate correction* (refused by default) and bit-identical to AFNI in reproduce mode.


## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, a night at a time: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest night:

{{ ev.random_testing('/tools/afni-automask/') }}

## Known limits {#limits}

LARMORX writes NIfTI only: AFNI's default prefix `automask` is its own dataset format, which both implementations refuse (an expected divergence). The clean-room original ignores AFNI's own header extension in an AFNI-written input (AFNI-10), as 3dTshift's original does; the replica reads it as AFNI does. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md).
