---
title: 3dTshift
kicker: Evidence · AFNI
lede: >-
  `3dTshift` shifts each slice's time series to one common time. LARMORX has two ports of it,
  both in `larmorx` itself. Of the 317 cases of its record, the replica gives AFNI 26.3.05's
  bytes in 282; both programs refuse 32, and 3 are expected divergences. Of its own 317, the
  clean room gives AFNI's bytes in 180 and differs in 102 only by the last bits of its Fourier
  shift, within the record's thresholds.
  On fMRIPrep's call the replica gives AFNI's and fMRIPrep's output bit for bit. Both ports
  correct AFNI's negative scale factor defect (AFNI-01) by default.
description: >-
  How LARMORX's two ports of AFNI's 3dTshift, the replica and the clean room, compare with AFNI
  26.3.05, AFNI 25.2.09 and fMRIPrep 25.2.6: fMRIPrep's slice-timing correction of a real BOLD
  run, the correction of a negative scale factor (AFNI-01), every case of the two records with
  its verdict, random testing and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0, with CC BY 4.0's attribution for the Medical College of Wisconsin's code</span>: translated from AFNI's source; in <code>pip install larmorx</code> since 2026-10-29, until then the separate GPL package <code>larmorx-gpl</code></li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: written from <a href="{{ repo('specs/3dTshift.md') }}">specs/3dTshift.md</a></li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span>; clean room <span class="status-tag status-tag--plain">validated</span> (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/afni-tshift-replica.md') }}">standard comparison</a> (AFNI 26.3.05) · the clean room's: <a href="{{ repo('docs/validation/afni-tshift.md') }}">standard comparison</a> (AFNI 26.3.05) · benchmark <a href="{{ repo('docs/benchmarks/afni-tshift.md') }}">afni-tshift</a></dd>
<dt>Reference</dt><dd><a href="{{ link('/programs/afni/3dTshift/') }}"><code>3dTshift</code></a> · API page <a href="{{ repo('docs/api/afni-tshift.md') }}">afni-tshift</a></dd>
</dl>

## What is compared {#what-it-is}

3dTshift shifts each slice's time series to a common time, so that the slices of a volume acquired at different moments can be treated as simultaneous. fMRIPrep calls it with the slice times of the BIDS sidecar and `-tzero` at the middle of the acquisition, with AFNI's default Fourier interpolation.

The two ports run beside AFNI 26.3.05's `3dTshift` and AFNI 25.2.09's on the same files with the same arguments, both AFNI releases the repository's builds; fMRIPrep's own output is the file it wrote in its run.

```bash
larmorx afni 3dTshift -ignore 0 -tpattern @slice_timing.1D -TR 2s -tzero 0.975 -prefix bold_stc.nii.gz bold.nii.gz
```

```python
import json
import larmorx as lx

meta = json.load(open("sub-01_task-rest_bold.json"))
times, t0 = lx.afni.fmriprep_slice_timing(meta["SliceTiming"], meta.get("SliceEncodingDirection"))
stc = lx.afni.tshift("sub-01_task-rest_bold.nii.gz", slice_times=times, tzero=t0,
                     tr=meta["RepetitionTime"], n_threads=8)
```

The call above leaves `implementation` at `"auto"`. The [API page](repo:docs/api/afni-tshift.md) maps every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

Since 2026-10-29 both ports are part of LARMORX itself (`pip install larmorx`). AFNI 26.3.05 releases the Medical College of Wisconsin's code, which these programs' results depend on, under CC BY 4.0. So the replica moved from the separate GPL package `larmorx-gpl` into LARMORX, under the Apache License with CC BY 4.0's attribution ([NOTICE](repo:NOTICE), [licensing](repo:docs/licensing.md)), and runs in the same process. The replica is translated from AFNI's source. The clean room is written without it, from a description of what the program does ([specs/3dTshift.md](repo:specs/3dTshift.md)).

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). On the command line, `larmorx --implementation clean-room afni 3dTshift ...` does the same from the next release; in 0.1.0rc1 it is the environment variable `LARMORX_IMPLEMENTATION`. `auto` takes the replica (before 2026-10-29 only where `larmorx-gpl` was installed, the clean room otherwise). The examples below were computed with the replica as the separate program it was then; the same files come out of it in the same process (its records, made again in the same process on 2026-10-29, agree case for case).

**The C library's last digits (since 2026-11-04).** With `-wsinc5` and `-wsinc9`, 3dTshift weights its neighbours by a windowed sinc whose `sinf` and `cosf` AFNI takes from glibc, the C library of Linux. glibc's results are now and then one unit in the last place away from the exact value rounded once. LARMORX computes them correctly rounded, the same on every platform. Since 2026-11-04 the clean room's `reproduce` computes them exactly as glibc 2.35 does, with LARMORX's versions of glibc's functions (`larmorx_core::math`), and both its `fix` and its `reproduce` name GLIBC-07 exactly where a weight differs (about 1 % of the weights; [register](repo:docs/findings/upstream-defects.md)). Two cases show it, `methods/glibc-sinf-wsinc5` and `methods/glibc-sinf-wsinc9`: slice times where the default's output differs from AFNI's in 2 and 14 values. In `reproduce` they are AFNI's bytes, and the replica's record has them too. fMRIPrep's calls interpolate by Fourier, which calls neither function: the examples below are unchanged, the clean room's runs giving the same bytes as before.

## The verdicts at a glance {#verdicts}

{{ ev.agreement('afni-tshift', 'replica') }}

{{ ev.agreement('afni-tshift', 'original') }}

Each record runs 317 cases against AFNI 26.3.05: the clean room's two cases of the weighted sinc's functions (above) joined its record on 2026-11-04, and the replica's record has had them since the same day. Since 2026-10-29 both ports follow **AFNI 26.3.05**, AFNI's newest release, and their records run against it, with AFNI 25.2.09 run beside it on every case (*AFNI's own step*): the replica since the version update, the clean room since its alignment the same day. Between the two releases this program changed in exactly two places, both corrections LARMORX already made by default: header slice code 2 read as NIfTI defines it (AFNI-03), and `-no_detrend` de-meaning every voxel (AFNI-05). In `reproduce` both ports now give 26.3.05's result there and name neither. The examples below show both versions' outputs: on fMRIPrep's calls they are the same bytes.

The replica gives AFNI's bytes in every case that produces an output, and AFNI's exit status and messages in the others. The clean room is bit-identical wherever it does not interpolate by Fourier, and within the record's thresholds where it does. AFNI computes the Fourier shift in float32 with its own FFT, the clean room in double precision, so float outputs differ in the last bits and integer outputs now and then round the other way, by one. Those differences are marked *open*: explained, small, and still closable.

## In fMRIPrep: the slice-timing correction of a real BOLD run {#example}

{{ ev.example('afni-tshift', 'fmriprep-stc') }}

## A deliberate correction: a negative scale factor (AFNI-01) {#correction}

The same run stored with a negative scale factor is the same data: every value is unchanged. AFNI applies that factor on output only, so its result comes out sign-flipped and scaled ([AFNI-01](repo:docs/findings/upstream-defects.md)). Both ports correct it by default, `fix`, and warn; `reproduce` gives AFNI's result.

{{ ev.example('afni-tshift', 'afni-01') }}

## Every case {#cases}

Each case of the two records, with what it tests, its command line, each port's verdict and the reason. Search, filter by category or verdict (or select a segment of a chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('afni-tshift') }}

## Speed {#speed}

{{ ev.speed('afni-tshift') }}

## Corrections by default {#corrections}

Where AFNI has a deterministic defect that changes a result, both ports correct it by default, `fix`, and warn. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives AFNI's behaviour, and the records compare with it. The records' lists of what `fix` changed meet AFNI-01, AFNI-02, AFNI-07, AFNI-08, AFNI-16, AFNI-19, AFNI-22 and AFNI-23 ([register](repo:docs/findings/upstream-defects.md)). AFNI-03 and AFNI-05 were AFNI 25.2.09's: AFNI 26.3.05 behaves as LARMORX corrected them.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original and both ports, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a case of the record, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/evidence/afni-tshift/', 'afni-tshift') }}

## Known limits {#limits}

LARMORX writes NIfTI only (a `-prefix` in AFNI's own format is refused), `-voxshift` is not supported, and a dataset of one row is written as NIfTI where AFNI writes a 1D text file (AFNI-20): the three expected divergences. Writing an existing output in place in a directory that cannot be written, as AFNI does, is planned.

## History {#history}

- **until 2026-10-29**: the replica followed AFNI 25.2.09, bit-identical to it in every compared case of its record.
- **2026-10-29**: AFNI 26.3.05 releases the Medical College of Wisconsin's code under CC BY 4.0; the replica moves from `larmorx-gpl` into `larmorx`, and both ports follow AFNI 26.3.05.
- **2026-11-04**: the clean room's `reproduce` computes `sinf` and `cosf` as glibc 2.35 does (GLIBC-07); the two cases of the weighted sinc's functions join both records.
- **2026-11-13**: the replica's record made again from a commit with no uncommitted changes, as every record must be (the record of 2026-11-04 was not): the same result in every one of its 317 cases.
