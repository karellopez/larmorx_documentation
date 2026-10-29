---
title: 3dTshift
kicker: Tools · AFNI
lede: >-
  Slice-timing correction in two implementations: an exact replica of AFNI's source in the
  separate larmorx-gpl package, bit-identical to AFNI 26.3.05 (and, before it, 25.2.09) in
  every compared case, and a
  clean-room original in LARMORX (Apache-2.0), written from a behavioural specification, which
  differs from AFNI by the last bits of its Fourier shift.
description: LARMORX's two implementations of AFNI's 3dTshift, validated against AFNI 26.3.05 (the replica), AFNI 25.2.09 and fMRIPrep 25.2.6 — a real BOLD run and a deliberate correction to inspect, every parity case with its verdict, and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-gpl</code>, GPL-3.0-or-later, run as a separate program); clean-room original (<code>larmorx</code>, Apache-2.0, from <a href="{{ repo('specs/3dTshift.md') }}">specs/3dTshift.md</a>)</dd>
<dt>Status</dt><dd><span class="status-tag eco-afni">validated</span> (each)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/afni-tshift-replica.md') }}">replica</a> · <a href="{{ repo('docs/validation/afni-tshift.md') }}">original</a> · benchmark <a href="{{ repo('docs/benchmarks/afni-tshift.md') }}">afni-tshift</a> · API <a href="{{ repo('docs/api/afni-tshift.md') }}">afni-tshift</a></dd>
</dl>

## What it is

3dTshift shifts each slice's time series to a common time, so that the slices of a volume acquired at different moments can be treated as simultaneous. fMRIPrep calls it with the slice times of the BIDS sidecar and `-tzero` at the middle of the acquisition, with AFNI's default Fourier interpolation.

```bash
larmorx afni 3dTshift -ignore 0 -tpattern @slice_timing.1D -TR 2s -tzero 0.975 -prefix bold_stc.nii.gz bold.nii.gz
```

```python
import json
import larmorx as lx

meta = json.load(open("sub-01_task-rest_bold.json"))
times, t0 = lx.afni.fmriprep_slice_timing(meta["SliceTiming"], meta.get("SliceEncodingDirection"))
stc = lx.afni.tshift("sub-01_task-rest_bold.nii.gz", slice_times=times, tzero=t0,
                     tr=meta["RepetitionTime"], n_threads=8)       # implementation="auto"
```

`implementation="auto" | "replica" | "original"` chooses (on the command line `LARMORX_IMPLEMENTATION`); `auto` takes the replica when `larmorx-gpl` is installed. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('afni-tshift', 'replica') }}

{{ ev.agreement('afni-tshift', 'original') }}

The clean-room original's record runs 315 cases against AFNI 25.2.09, the replica's 315 against AFNI 26.3.05. Since 2026-10-29 the replica follows **AFNI 26.3.05**, AFNI's newest release, and its record runs against it, with AFNI 25.2.09 run beside it on every case (*AFNI's own step*); the clean-room original's record stays on AFNI 25.2.09 until it follows 26.3.05's two fixes. Between the two releases these programs changed in exactly two places, both corrections LARMORX already made by default: header slice code 2 read as NIfTI defines it (AFNI-03) and 3dTshift's `-no_detrend` de-meaning every voxel (AFNI-05). The examples below show both versions' outputs: on fMRIPrep's calls they are the same bytes. The replica gives AFNI's bytes in every case that produces an output, and AFNI's exit status and messages in the others. The clean-room original is bit-identical wherever it does not interpolate by Fourier, and within the record's thresholds where it does: AFNI computes the Fourier shift in float32 with its own FFT, the original in double precision, so float outputs differ in the last bits and integer outputs occasionally round the other way, by one. Those differences are marked *open*: explained, small, and still closable.

## A real BOLD run, as fMRIPrep corrects it {#example}

{{ ev.example('afni-tshift', 'fmriprep-stc') }}

## A deliberate correction: AFNI-01 {#correction}

The same run stored with a negative scale factor is the same data: every value is unchanged. AFNI applies that factor on output only, so its result comes out sign-flipped and scaled ([AFNI-01](repo:docs/findings/upstream-defects.md)). Both LARMORX implementations correct it by default and warn; `reproduce` gives AFNI's result.

{{ ev.example('afni-tshift', 'afni-01') }}

## Every case {#cases}

Each case of the two records, with what it tests, its command line, the verdict of each implementation and the reason. Search, filter (or select a segment of a chart above), sort; `#case=<name>` links to one.

{{ ev.cases('afni-tshift') }}

## Speed {#speed}

{{ ev.speed('afni-tshift') }}

## Corrections by default {#corrections}

Both implementations correct AFNI's deterministic defects by default and warn: the records' fix passes meet AFNI-01, AFNI-02, AFNI-03, AFNI-05, AFNI-07, AFNI-08, AFNI-16, AFNI-19, AFNI-22 and AFNI-23, with `upstream_defects="reproduce"` giving AFNI's behaviour ([register](repo:docs/findings/upstream-defects.md)).

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/afni-tshift/') }}

## Known limits {#limits}

LARMORX writes NIfTI only (a `-prefix` in AFNI's own format is refused), `-voxshift` is not supported, and a dataset of one row is written as NIfTI where AFNI writes a 1D text file (AFNI-20): the three expected divergences. Writing in place an existing output in a directory that cannot be written, as AFNI does, is planned.
