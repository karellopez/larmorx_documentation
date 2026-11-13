---
title: 3dAutomask
kicker: Evidence · AFNI
lede: >-
  `3dAutomask` makes a brain mask of an EPI series or a skull-stripped image from its
  intensities alone. LARMORX has two ports of it, both in `larmorx` itself, and both give AFNI
  26.3.05's masks bit for bit in every compared case, fMRIPrep's own calls included. The
  replica's record has 125 cases. The clean room's has 130; in 14 of them, fMRIPrep's calls on
  images AFNI wrote, its header differs from AFNI's where AFNI reads the geometry from its own
  header extension, in 7 significant digits (AFNI-10); its masks are AFNI's.
description: >-
  How LARMORX's two ports of AFNI's 3dAutomask, the replica and the clean room, compare with
  AFNI 26.3.05, AFNI 25.2.09 and fMRIPrep 25.2.6: fMRIPrep's skull strip of a real BOLD
  reference, a raw BOLD series, the correction of -peels 0 (AFNI-43), a child's run of the data
  panel with extreme head motion, every case of the two records with its verdict, random testing
  and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0, with CC BY 4.0's attribution for the Medical College of Wisconsin's code</span>: translated from AFNI's source; in <code>pip install larmorx</code> since 2026-10-29, until then the separate GPL package <code>larmorx-gpl</code></li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: written from <a href="{{ repo('specs/3dAutomask.md') }}">specs/3dAutomask.md</a></li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span>; clean room <span class="status-tag status-tag--plain">validated</span> (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/afni-automask-replica.md') }}">standard comparison</a> (AFNI 26.3.05) · the clean room's: <a href="{{ repo('docs/validation/afni-automask.md') }}">standard comparison</a> (AFNI 26.3.05) · findings <a href="{{ repo('docs/findings/afni-masks-clean-room.md') }}">afni-masks-clean-room</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/afni-automask.md') }}">afni-automask</a></dd>
</dl>

## What is compared {#what-it-is}

3dAutomask makes a brain mask from the intensities alone. It averages the absolute values of a series' volumes, finds a clip level from their histogram (gradually, octant by octant, unless `-nograd`), keeps the largest connected cluster above it, peels and unpeels it to cut off thin protrusions, and fills its holes. fMRIPrep calls it once per BOLD run, on its unifized BOLD reference, with `-dilate 1` and `-apply_prefix`: the second skull strip of its BOLD reference workflow.

The two ports run beside AFNI 26.3.05's `3dAutomask` and AFNI 25.2.09's on the same files with the same arguments, both AFNI releases the repository's builds, and beside fMRIPrep's own build of AFNI in its image.

```bash
larmorx afni 3dAutomask -apply_prefix uni_xform_masked.nii.gz -dilate 1 -prefix uni_xform_mask.nii.gz uni_xform.nii.gz
```

```python
import larmorx as lx

r = lx.afni.automask("uni_xform.nii.gz", dilate=1, apply=True)
r.mask, r.masked
```

The call above leaves `implementation` at `"auto"`. The [API page](repo:docs/api/afni-automask.md) maps every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

3dAutomask's results depend on AFNI library routines copyrighted by the Medical College of Wisconsin, GPL-2 until AFNI 25.2.09, so LARMORX has two ports of it. Since 2026-10-29 both are part of LARMORX itself (`pip install larmorx`). AFNI 26.3.05 releases the Medical College of Wisconsin's code, which these programs' results depend on, under CC BY 4.0. So the replica moved from the separate GPL package `larmorx-gpl` into LARMORX, under the Apache License with CC BY 4.0's attribution ([NOTICE](repo:NOTICE), [licensing](repo:docs/licensing.md)), and runs in the same process. The replica is translated from AFNI's source. The clean room is written without it, from a description of what the program does ([specs/3dAutomask.md](repo:specs/3dAutomask.md)).

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). On the command line, `larmorx --implementation clean-room afni 3dAutomask ...` does the same from the next release; in 0.1.0rc1 it is the environment variable `LARMORX_IMPLEMENTATION`. `auto` takes the replica (before 2026-10-29 only where `larmorx-gpl` was installed, the clean room otherwise). The examples below were computed with the replica as the separate program it was then; its records, made again in the same process on 2026-10-29, agree case for case.

The clean room decides each pass of its mask operations voxel by voxel in parallel, finds clusters by union-find over runs of voxels, and replaces two of AFNI's repeated sweeps by breadth-first searches with the same result. Its result does not depend on the thread count.

## The verdicts at a glance {#verdicts}

{{ ev.agreement('afni-automask', 'replica') }}

{{ ev.agreement('afni-automask', 'original') }}

The clean room's record runs 130 cases against AFNI 26.3.05, the replica's 125. Since 2026-10-29 both ports follow **AFNI 26.3.05**, AFNI's newest release, and their records run against it, with AFNI 25.2.09 run beside it on every case (*AFNI's own step*): the replica since the version update, the clean room since its alignment the same day. Between the two releases these programs changed in exactly two places, both corrections LARMORX already made by default: header slice code 2 read as NIfTI defines it (AFNI-03), and 3dTshift's `-no_detrend` de-meaning every voxel (AFNI-05). In `reproduce` both ports now give 26.3.05's result there and name neither. The examples below show both versions' outputs: on fMRIPrep's calls they are the same bytes.

The replica gives AFNI's bytes, data and NIfTI header, in every case that writes an output, and AFNI's exit status and messages in every case. So does the clean room, but in 14 cases: fMRIPrep's calls on its 3dUnifize outputs, which carry AFNI's own header extension, where the header differs in 7 significant digits (AFNI-10, a *deliberate correction*); its masks are AFNI's. Where AFNI crashes on a missing option value (AFNI-40), both ports stop with an error instead: the expected divergences. Each case is also run in `fix`, the default, where LARMORX corrects AFNI's deterministic defects and names them.

## In fMRIPrep: the BOLD reference's second skull strip {#example}

fMRIPrep's own call on one of its runs, given to AFNI, to fMRIPrep's build of AFNI, to the replica and to the clean room (at 1 and 6 threads). Each mask is drawn over the image it was made from; choose *Masked input* above the panels for `-apply_prefix`'s output, and the difference panels for what separates two runs.

{{ ev.example('afni-automask', 'fmriprep-automask') }}

## A raw BOLD series {#bold}

The functional path: with several volumes, 3dAutomask first averages their absolute values, then masks the average.

{{ ev.example('afni-automask', 'bold-automask') }}

## A deliberate correction: `-peels 0` (AFNI-43) {#correction}

3dAutomask's help says `-peels 0` turns the peeling off; AFNI peels once instead ([AFNI-43](repo:docs/findings/upstream-defects.md)). Both ports' default, `fix`, does not peel, and warns; `reproduce` gives AFNI's mask.

{{ ev.example('afni-automask', 'afni-43') }}

## On the data panel: extreme head motion {#panel}

The first case of the [data panel](/validation/data-panel/) on this page, added beside the examples above: AFNI's default on a child's resting-state run with extreme head motion (OpenNeuro ds000256), the whole field of view shown, its noise and the masks' edges included. Like every panel case that is not one of a program's key datasets, it is stored as three full-resolution slices through the voxel where the comparison differs most (the field's centre where nothing differs); its metrics are over every voxel.

{{ ev.example('afni-automask', 'panel-ds000256-motion') }}

## Every case {#cases}

Each case of the two records, with what it tests, its command line, each port's verdict and the reason. Search, filter by category or verdict (or select a segment of a chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('afni-automask') }}

## Speed {#speed}

{{ ev.speed('afni-automask') }}

3dAutomask is quick in every port: its time is mostly reading and writing compressed NIfTI, and AFNI's is single-threaded. These are informal timings on a shared machine ([findings](repo:docs/findings/afni-masks-clean-room.md)); there is no benchmark report yet.

## Corrections by default {#corrections}

Where AFNI has a deterministic defect that changes a result, both ports correct it by default, `fix`, and warn. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives AFNI's behaviour, and the records compare with it. The records' lists of what `fix` changed meet AFNI-43 (`-peels 0`), AFNI-01 (a negative scale factor dropped while averaging a series) and the dataset defects 3dAutomask shares with 3dTshift (AFNI-02, AFNI-07, AFNI-11, AFNI-12, AFNI-16, AFNI-18, AFNI-23, AFNI-26) ([register](repo:docs/findings/upstream-defects.md)). AFNI-41 (`-nbhrs` outside 6 to 26, silently 17 in AFNI) is refused by default before any input is read, in the same words by both ports (decided 2026-10-23), with `reproduce` giving AFNI's mask. AFNI-42 (`-NN1/2/3` reset the peel threshold) and AFNI-44 (the large-hole filling decided by the number of slices) are kept as AFNI's and documented.

**Refused by default: AFNI-41.** `-nbhrs` takes a value between 6 and 26, as the help says; outside that range AFNI accepts it silently and peels as with 17. A value outside the range makes no sense, and the project's rule for that case (2026-10-23) is a clear error: by default the replica stops with a message naming AFNI-41, before reading the input; in `reproduce` it gives AFNI's mask, bit for bit. The case explorer shows it: [options/nbhrs-40](#case=options/nbhrs-40), and in the standard comparison `nbhrs-5`, `nbhrs-27`, `nbhrs-0` and `nbhrs-40-then-NN1`, each with the verdict *deliberate correction* (refused by default) and bit-identical to AFNI in `reproduce`.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original and both ports, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a case of the record, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/evidence/afni-automask/', 'afni-automask') }}

## Known limits {#limits}

LARMORX writes NIfTI only: AFNI's default prefix `automask` is its own dataset format, which both ports refuse (an expected divergence). The clean room ignores AFNI's own header extension in an AFNI-written input (AFNI-10), as 3dTshift's clean room does; the replica reads it as AFNI does. The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output.

## History {#history}

- **2026-10-23**: AFNI-41 refused by default, by the project's rule for an input that makes no sense.
- **2026-10-29**: AFNI 26.3.05 releases the Medical College of Wisconsin's code under CC BY 4.0; the replica moves from `larmorx-gpl` into `larmorx`, and both ports follow AFNI 26.3.05.
- **2026-10-30**: both records made again against AFNI 26.3.05: 130 and 125 cases.
