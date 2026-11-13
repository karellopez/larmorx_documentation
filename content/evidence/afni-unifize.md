---
title: 3dUnifize
kicker: Evidence · AFNI
lede: >-
  `3dUnifize` makes a T1w's white matter uniform (or, with -T2, a T2w's or an EPI image's).
  LARMORX has two ports of it, both in `larmorx` itself. The replica gives AFNI 26.3.05's bytes
  in all 97 compared cases of its record that write outputs, fMRIPrep's own calls included. The
  clean room gives them in 44 of its 99, and in the other 55 once AFNI uses correctly rounded
  maths: a few squashed values differ in their last bit where glibc's `tanhf` is not correctly
  rounded.
description: >-
  How LARMORX's two ports of AFNI's 3dUnifize, the replica and the clean room, compare with
  AFNI 26.3.05, AFNI 25.2.09 and fMRIPrep 25.2.6: fMRIPrep's uniformization of a real BOLD
  reference, a real T1w on the half-size path, the correction of -T2up 100 (AFNI-45), AFNI at 1
  and 6 threads and with correctly rounded maths, every case of the two records with its
  verdict, random testing and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0, with CC BY 4.0's attribution for the Medical College of Wisconsin's code</span>: translated from AFNI's source; in <code>pip install larmorx</code> since 2026-10-29, until then the separate GPL package <code>larmorx-gpl</code></li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: written from <a href="{{ repo('specs/3dUnifize.md') }}">specs/3dUnifize.md</a></li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span>; clean room <span class="status-tag status-tag--plain">validated</span> (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/afni-unifize-replica.md') }}">standard comparison</a> (AFNI 26.3.05) · the clean room's: <a href="{{ repo('docs/validation/afni-unifize.md') }}">standard comparison</a> (AFNI 26.3.05) · findings <a href="{{ repo('docs/findings/afni-masks-clean-room.md') }}">afni-masks-clean-room</a></dd>
<dt>Reference</dt><dd><a href="{{ link('/programs/afni/3dUnifize/') }}"><code>3dUnifize</code></a> · API page <a href="{{ repo('docs/api/afni-unifize.md') }}">afni-unifize</a></dd>
</dl>

## What is compared {#what-it-is}

3dUnifize divides each voxel by the local white-matter level, a mean of the upper percentiles of the masked values in a ball around it (`-Urad`, 18.3 voxels across by default, whatever the voxel size; on a half-size copy above a million voxels), scales white matter to 1000 and squashes the brightest values. With `-T2` it inverts the contrast first and back after; `-GM` also scales grey matter; `-EPI` works volume by volume. fMRIPrep calls it once per BOLD run, with `-T2`, on its skull-stripped BOLD reference, before the second skull strip ([3dAutomask](/evidence/afni-automask/)).

The two ports run beside AFNI 26.3.05's `3dUnifize` and AFNI 25.2.09's on the same files with the same arguments, both AFNI releases the repository's builds, at one and six OpenMP threads and with correctly rounded maths; fMRIPrep's own output is the file it wrote in its run.

```bash
larmorx afni 3dUnifize -clfrac 0.2 -rbt 18.3 65.0 90.0 -prefix uni.nii.gz -T2 -input ref_brain.nii.gz
```

```python
import larmorx as lx

uni = lx.afni.unifize("ref_brain.nii.gz", **lx.afni.fmriprep_unifize_options(), n_threads=6)
t1 = lx.afni.unifize("sub-01_T1w.nii.gz", save_scale=True)
```

The calls above leave `implementation` at `"auto"`. The [API page](repo:docs/api/afni-unifize.md) maps every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

3dUnifize's results depend on AFNI library routines copyrighted by the Medical College of Wisconsin, GPL-2 until AFNI 25.2.09, so LARMORX has two ports of it. Since 2026-10-29 both are part of LARMORX itself (`pip install larmorx`). AFNI 26.3.05 releases the Medical College of Wisconsin's code, which these programs' results depend on, under CC BY 4.0. So the replica moved from the separate GPL package `larmorx-gpl` into LARMORX, under the Apache License with CC BY 4.0's attribution ([NOTICE](repo:NOTICE), [licensing](repo:docs/licensing.md)), and runs in the same process. The replica is translated from AFNI's source. The clean room is written without it, from a description of what the program does ([specs/3dUnifize.md](repo:specs/3dUnifize.md)).

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). On the command line, `larmorx --implementation clean-room afni 3dUnifize ...` does the same from the next release; in 0.1.0rc1 it is the environment variable `LARMORX_IMPLEMENTATION`. `auto` takes the replica (before 2026-10-29 only where `larmorx-gpl` was installed, the clean room otherwise). The examples below were computed with the replica as the separate program it was then; its records, made again in the same process on 2026-10-29, agree case for case.

**The C library's functions.** The squash calls `tanhf`: the replica carries fdlibm's, as glibc 2.35 runs it, checked against glibc on all 2<sup>32</sup> float inputs. `-EPI`'s radius calls `cbrtf`, whose glibc code is not part of LARMORX: the replica computes it correctly rounded and warns on the voxel sizes where the cube root's last bit could change the result (2,953 of the float voxel volumes between 1 and 100 mm³; on 80 of them glibc's last bit changes the ball of neighbours). The clean room uses a correctly rounded `tanhf` (a port of CORE-MATH's), as LARMORX's own maths does wherever it is not following glibc on purpose.

**The clean room's speed.** Its ball percentiles are its speed: instead of gathering and sorting some 25,000 values at every voxel, it slides a window of counts per rank from voxel to voxel, changing only the ball's two surfaces, and reads the values between the two percentiles in ascending order, which gives the specification's sum exactly. Planes run in parallel, with the same bytes at any thread count.

## The verdicts at a glance {#verdicts}

{{ ev.agreement('afni-unifize', 'replica') }}

{{ ev.agreement('afni-unifize', 'original') }}

The clean room's record runs 129 cases and the replica's 127, both against AFNI 26.3.05 (the version step below), with AFNI's exit status and messages in every case. The replica gives AFNI's bytes in every case that writes an output, 97 of 97. The clean room gives them in 44 of the 99 compared cases that write outputs. In the other 55 its headers are AFNI's and a few squashed values (above 1300) differ in their last bit, at most 1,633 values of a T1w and 8.7 × 10<sup>−8</sup> of the largest value, against a threshold of 10<sup>−5</sup>: AFNI's squash calls glibc's `tanhf`, which is not correctly rounded on some arguments, the clean room's is. Run with CORE-MATH's correctly rounded functions preloaded, AFNI gives the clean room's bytes in all 55 (*identical with correctly rounded maths*). AFNI computes every voxel's local level independently in its OpenMP loop: its result does not depend on the thread count, and neither does either port's. Where AFNI crashes (AFNI-40, AFNI-46), both stop with an error instead; where AFNI reads past the end of its half-size scale image (AFNI-47, a volume of more than a million voxels only two slices thick), AFNI crashed in our runs and both define the result.

Since 2026-10-29 both ports follow **AFNI 26.3.05**, AFNI's newest release, and their records run against it, with AFNI 25.2.09 run beside it on every case (*AFNI's own step*): the replica since the version update, the clean room since its alignment the same day. Between the two releases these programs changed in exactly two places, both corrections LARMORX already made by default: header slice code 2 read as NIfTI defines it (AFNI-03), and 3dTshift's `-no_detrend` de-meaning every voxel (AFNI-05). In `reproduce` both ports now give 26.3.05's result there and name neither. The examples below show both versions' outputs: on fMRIPrep's calls they are the same bytes.

## In fMRIPrep: the uniformization of a BOLD reference {#example}

fMRIPrep's own call on one of its runs, given to AFNI at one and six OpenMP threads and to the replica at one and six threads in `fix` and `reproduce`, beside the output fMRIPrep produced in its run; then to the clean room at one and six threads in `fix` and `reproduce`, and to AFNI with CORE-MATH's correctly rounded functions preloaded.

{{ ev.example('afni-unifize', 'fmriprep-unifize') }}

## A T1w, on the half-size path {#t1w}

Above a million voxels, 3dUnifize computes the local white-matter level on a half-size copy and brings it back; choose *Scale image* above the panels for the factor each voxel is multiplied by.

{{ ev.example('afni-unifize', 't1w-unifize') }}

## A deliberate correction: `-T2up 100` (AFNI-45) {#correction}

At `-T2up 100`, the upper percentile 3dUnifize inverts about is read one past the end of the sorted values ([AFNI-45](repo:docs/findings/upstream-defects.md)): what AFNI finds there is memory it never wrote. Both ports' default, `fix`, inverts about the largest value, and warns; `reproduce` fills the read with 0, as AFNI read it here.

{{ ev.example('afni-unifize', 'afni-45') }}

## Every case {#cases}

Each case of the two records, with what it tests, its command line, each port's verdict and the reason. Search, filter by category or verdict (or select a segment of a chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('afni-unifize') }}

## Speed {#speed}

{{ ev.speed('afni-unifize') }}

The clean room is 4 to 25 times faster than AFNI at the same thread count, and 3 to 10 times faster than the replica, which computes as AFNI does: its ball percentiles slide from voxel to voxel instead of being gathered and sorted at every voxel. On the half-size path the ball works on an eighth of the voxels, and reading and writing the full-size compressed images takes a larger share of the time. These are informal timings on a shared machine ([findings](repo:docs/findings/afni-masks-clean-room.md)); there is no benchmark report yet.

## Corrections by default {#corrections}

Where AFNI has a deterministic defect that changes a result, both ports correct it by default, `fix`, and warn. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives AFNI's behaviour, and the records compare with it. The records' lists of what `fix` changed meet AFNI-45 (`-T2up` near 100), AFNI-47 (a volume of more than a million voxels with an axis of 2 or 3), AFNI-01 (`-EPI`'s median of a series with a negative scale factor) and the dataset defects 3dUnifize shares with 3dTshift (AFNI-02, AFNI-07, AFNI-11, AFNI-12, AFNI-16, AFNI-18, AFNI-23, AFNI-26) ([register](repo:docs/findings/upstream-defects.md)). AFNI-48 (`-T2` given three times without `-EPI`, which leaves the output inverted) is refused by default, in the same words by both ports (decided 2026-10-23), with `reproduce` giving AFNI's output.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original and both ports, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a case of the record, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/evidence/afni-unifize/', 'afni-unifize') }}

## Known limits {#limits}

LARMORX writes NIfTI only: AFNI's default prefix `Unifized` is its own dataset format, which both ports refuse (an expected divergence). The clean room's squashed values (above 1300) can differ from AFNI's in their last bit where glibc's `tanhf` is not correctly rounded; AFNI with correctly rounded maths gives the clean room's bytes. There is no benchmark report yet. The cross-platform checks cannot reach the half-size path (more than a million voxels, beyond their 32³ budget); the records cover it on real T1w images. The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output.

## History {#history}

- **2026-10-23**: AFNI-48 refused by default, by the project's rule for an input that makes no sense.
- **2026-10-29**: AFNI 26.3.05 releases the Medical College of Wisconsin's code under CC BY 4.0; the replica moves from `larmorx-gpl` into `larmorx`, and both ports follow AFNI 26.3.05.
- **2026-10-30**: both records made again against AFNI 26.3.05: 129 and 127 cases.
