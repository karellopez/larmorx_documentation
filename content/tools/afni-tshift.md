---
title: 3dTshift
kicker: Tools · AFNI
lede: >-
  Slice-timing correction in two implementations: a clean-room original in LARMORX
  (Apache-2.0), written from a behavioural specification, and an exact replica of AFNI's
  source in the separate larmorx-gpl package.
description: LARMORX's two implementations of AFNI's 3dTshift, the clean-room original and the GPL replica, their validation against AFNI 25.2.09 in figures, a real BOLD run, and speed.
---

<dl class="facts">
<dt>Implementations</dt><dd>clean-room original (<code>larmorx</code>, Apache-2.0, from <a href="{{ repo('specs/3dTshift.md') }}">specs/3dTshift.md</a>); exact replica (<code>larmorx-gpl</code>, GPL-3.0-or-later, run as a separate program)</dd>
<dt>Status</dt><dd><span class="status-tag eco-afni">validated</span> (each)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/afni-tshift.md') }}">original</a> · <a href="{{ repo('docs/validation/afni-tshift-replica.md') }}">replica</a> · benchmark <a href="{{ repo('docs/benchmarks/afni-tshift.md') }}">afni-tshift</a> · API <a href="{{ repo('docs/api/afni-tshift.md') }}">afni-tshift</a></dd>
</dl>

## What it is

3dTshift shifts each slice's time series to a common time, so that the slices of a volume acquired at different moments can be treated as simultaneous. fMRIPrep calls it with the slice times of the BIDS sidecar and `-tzero` at the middle of the acquisition, with AFNI's default Fourier interpolation.

## How to call it

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

`implementation="auto" | "replica" | "original"` chooses (on the command line `LARMORX_IMPLEMENTATION`); `auto` takes the replica when `larmorx-gpl` is installed.

## Agreement with AFNI

Both records run the same 314 cases against AFNI 25.2.09: 279 pass, 32 are rejected by both programs and 3 are expected divergences. The **replica** is bit-identical in 279 of 279. The **clean-room original** is bit-identical in 176 of 279 and within the record's thresholds in the rest: its Lagrange and weighted-sinc methods and copies in 129 of 132, its Fourier interpolation in 47 of 147, because AFNI computes the FFT in float32 with its own kernels and the original in double precision, so float outputs differ in the last bits and integer outputs occasionally round the other way, by one. AFNI's global options and environment variables give the same messages, byte for byte, in all 63 cases that test them.

{{ figure('afni-tshift/agreement', "The clean-room original: the record's 314 cases by category, bit-identical to AFNI's output or within the record's thresholds (last float bits, integers by one), expected divergences and the inputs both refuse.") }}

{{ figure('afni-tshift/agreement-replica', "The replica (`larmorx-gpl`): the same 314 cases, every compared case bit-identical to AFNI.") }}

## A real BOLD run

{{ figure('afni-tshift/time-series', "fMRIPrep's 3dTshift command on OpenNeuro ds005040 sub-002's BOLD run (CC0-1.0; ascending slices over 1.95 s, TR 2 s, shifted to 0.975 s), by AFNI 25.2.09, the clean-room original and the replica. Top: one voxel of a late slice, at its acquisition times and shifted; the three outputs coincide. Bottom: per volume, the brain voxels (inside fMRIPrep's mask) whose stored int16 value differs from AFNI's: the original's differ by one unit (the Fourier rounding above), the replica's never.") }}

## Speed

{{ figure('afni-tshift/speed', "Median seconds of the whole command (reading, slice timing, writing) for AFNI's 3dTshift (single-threaded), the clean-room original and the replica at 1 and 12 threads, on three real BOLD runs, from the benchmark report of 2026-10-10 (Intel i7-8750H, 12 logical CPUs); the factor is the original's speed-up over AFNI at one thread.") }}

## Corrections by default

Both implementations correct AFNI's deterministic defects by default and warn: the records' fix passes meet AFNI-01, AFNI-02, AFNI-03, AFNI-05, AFNI-07, AFNI-08, AFNI-16, AFNI-19, AFNI-22 and AFNI-23, with `upstream_defects="reproduce"` giving AFNI's behaviour ([register](repo:docs/findings/upstream-defects.md)).

## Known limits

LARMORX writes NIfTI only (a `-prefix` in AFNI's own format is refused), `-voxshift` is not supported, and a dataset of one row is written as NIfTI where AFNI writes a 1D text file (AFNI-20). Writing in place an existing output in a directory that cannot be written, as AFNI does, is planned.
