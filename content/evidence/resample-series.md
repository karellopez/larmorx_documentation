---
title: One-shot BOLD resampler
kicker: Evidence · fMRIPrep
lede: >-
  fMRIPrep resamples each BOLD volume once, from the original series to every output space: head
  motion, distortion correction and the registrations in one interpolation. LARMORX's port is a
  replica of fMRIPrep's `ResampleSeries` with nitransforms' transform chains and SciPy's
  interpolation, following SciPy 1.18.1 and numpy 2.5.4 since 2026-10-29. In `reproduce` it gives
  the original's values bit for bit in 136 of its 137 compared cases, out of 139, and fMRIPrep's
  own output of a real run with its field map. In the other, coordinates beyond the range of
  64-bit integers, SciPy's C code is undefined and the replica returns NaN. Its default, `fix`, corrects
  fMRIPrep's Jacobian on other grids (PIPE-03), with fMRIPrep's result on request. On one thread
  it takes 4.1 to 5.2 times less time than fMRIPrep.
description: >-
  How LARMORX's replica of fMRIPrep's one-shot BOLD resampler (ResampleSeries, nitransforms'
  transform chains, SciPy's interpolation) compares with fMRIPrep's development version 26.0.0.dev1
  (ResampleSeries), nitransforms 25.1.0 and SciPy 1.18.1 with numpy 2.5.4 (and the step from SciPy 1.15.3 and numpy 2.3.5): fMRIPrep 25.2.6's
  resampling of a real run with its field map, PIPE-03's Jacobian against a reference computed
  another way, every case of the record with its verdict, random testing and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crates <code>larmorx-transform</code> and <code>larmorx-interp</code>, <code>lx.transforms.resample_series</code>, translated from fMRIPrep's <code>ResampleSeries</code> (fMRIPrep at commit 21a490fb, Apache-2.0), nitransforms 25.1.0's transform chains (MIT) and SciPy's <code>map_coordinates</code> (BSD-3-Clause)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span> (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/resample-series.md') }}">standard comparison</a> (fMRIPrep 26.0.0.dev1's <code>ResampleSeries</code>, nitransforms 25.1.0, SciPy 1.18.1) · <a href="{{ repo('docs/validation/resample-series-jacobian.md') }}">PIPE-03 on real geometry</a> · benchmark <a href="{{ repo('docs/benchmarks/resample-series.md') }}">resample-series</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/resample-series.md') }}">resample-series</a></dd>
</dl>

## What is compared {#what-it-is}

fMRIPrep resamples each BOLD volume once, from the original series to every output space. It composes the head-motion transform, the voxel-shift map of the field map along the phase-encoding axis, the registration to the T1w and, for standard spaces, the T1w-to-template warp. It applies them in one cubic B-spline interpolation, with the Jacobian of the distortion correction. This Python code is fMRIPrep's heaviest computation.

The record's original is fMRIPrep's `ResampleSeries` as installed in the comparison's Python environments (fMRIPrep's development version 26.0.0.dev1, at commit 21a490fb), run in-process through nipype, with nitransforms 25.1.0 and SciPy 1.18.1. The worked example also compares the replica with the file fMRIPrep 25.2.6 wrote in its own run.

```python
import json
import larmorx as lx

meta = json.load(open("sub-01_task-rest_bold.json"))
bold = lx.transforms.resample_series(
    "sub-01_task-rest_desc-stc_bold.nii.gz",
    "sub-01_task-rest_desc-coreg_boldref.nii.gz",
    ["sub-01_task-rest_from-orig_to-boldref_mode-image_desc-hmc_xfm.txt"],
    fieldmap="sub-01_fmapid-auto00000_desc-coeff_fieldmap.nii.gz", pe_dir="j",
    ro_time=meta["TotalReadoutTime"], jacobian=True, n_threads=8,
)
```

The [API page](repo:docs/api/resample-series.md) describes every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its port {#ports}

fMRIPrep comes under the Apache-2.0 licence, nitransforms under MIT and SciPy under BSD-3-Clause, so the replica is in `larmorx` itself, translated bit for bit as ANTs and sdcflows are:

- fMRIPrep's `resample_series` and its voxel-shift map and Jacobian (`fmriprep/interfaces/resampling.py`) in `larmorx-transform`, which computes the coordinates once per run and resamples the volumes on the call's threads;
- nitransforms' chains of transforms (affines, ITK's head-motion lists, dense fields from `.h5` composites) with their float32 parsing and LPS-to-RAS conversions;
- SciPy's `map_coordinates` and spline filters in `larmorx-interp`, their operation order kept, so the values are SciPy 1.18.1's.

A clean room of fMRIPrep's steps is planned after FreeSurfer ([roadmap](/roadmap/)).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('resample-series', 'port') }}

The [record](repo:docs/validation/resample-series.md) runs its cases in-process against fMRIPrep's `ResampleSeries`, nitransforms and SciPy, with `upstream_defects="reproduce"`. 136 of the 137 compared cases are bit-identical to their original. The other is the expected divergence: coordinates beyond the range of 64-bit integers, where SciPy's C code is undefined; the replica returns NaN there. Two cases, inputs in the wrong order or number, are refused by both with a `ValueError`.

Since the version update of 2026-10-29 the record runs against the newest releases, SciPy 1.18.1 and numpy 2.5.4 with OpenBLAS 0.3.34. They are kept in a Python environment of their own beside the one the other comparisons share (SciPy 1.15.3, numpy 2.3.5). Each case also runs its original under the older releases and says what changed between them, and why:

- 122 of the 136 compared cases give the same values;
- 14 change, every one through SciPy's own fix of the `reflect` boundary (SCI-03, [below](#corrections)): `map_coordinates` and the spline filters in modes `reflect`, `grid-mirror` and `nearest`, orders 2 to 5, where the replica follows SciPy 1.18.1;
- numpy's new release changes nothing the replica follows: its 4 × 4 products and inverses, checked on 18 million results.

## A worked example: fMRIPrep's resampling with a field map {#example}

fMRIPrep's resampler also ran here on the node's inputs, once with the newest releases and once with the shared environment's (a panel each). On this call (mode `grid-constant`) the two give the same values, every one, and the replica's output is theirs.

{{ ev.example('resample-series', 'fmriprep-native') }}

## PIPE-03: the Jacobian on another grid {#pipe-03}

On the BOLD's own grid, above, fMRIPrep's Jacobian is the right factor, and `fix` and `reproduce` give the same bytes. fMRIPrep resamples the same run onto T1w and template grids in the same step. There it differentiates the voxel-shift map along the wrong axis and in the wrong units ([register](repo:docs/findings/upstream-defects.md), PIPE-03). By default the replica takes the derivative along the BOLD's phase-encoding axis, in its voxels. The [record](repo:docs/validation/resample-series-jacobian.md) measures both factors on every grid of three fMRIPrep runs: against the exact factor of a synthetic field on ds000005's grids, and on ds005040's and ds005454's own field maps against the factor on the BOLD's own grid, carried to each grid.

{{ ev.example('resample-series', 'pipe-03') }}

## Every case {#cases}

Each case of the record, with what it tests, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('resample-series') }}

## Speed {#speed}

The benchmark ([report](repo:docs/benchmarks/resample-series.md)) times the resampling as fMRIPrep's `ResampleSeries` does it, without the file I/O, on real BOLD runs, and compares every output with fMRIPrep's, value by value.

{{ ev.speed('resample-series') }}

## Corrections by default {#corrections}

- **PIPE-03** (fMRIPrep's Jacobian on other grids) is corrected by default; `upstream_defects="reproduce"` gives fMRIPrep's result bit for bit ([register](repo:docs/findings/upstream-defects.md)). A report of PIPE-03 for fMRIPrep is drafted, not yet filed.
- **SCI-02** (SciPy's `map_coordinates` answers undefined float-to-integer conversions as x86-64 does): the replica clamps them and warns by default; `reproduce` gives x86-64's answers. The record's `fix` pass met it in 10 cases.
- **SCI-03** (SciPy's `reflect`, `grid-mirror` and `nearest` splines missing the samples on short axes, up to SciPy 1.17) was corrected by default from 2026-10-11. SciPy 1.18 fixed it, and the replica follows SciPy 1.18.1's fix in `fix` and in `reproduce` since 2026-10-29.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through fMRIPrep's resampler and the replica, in long runs of several hours. The inputs come from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), the options in random combinations from those the resampler accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a permanent case, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/evidence/resample-series/', 'resample-series') }}

## Known limits {#limits}

The replica covers fMRIPrep's one-shot path. The field-map estimation before it is sdcflows', on [its own pages](/evidence/sdcflows-fieldmap/) ([PEPOLAR, direct and fieldmap-less](/evidence/sdcflows-estimation/)); the rest of fMRIPrep's BOLD workflow comes with larmorprepx, LARMORX's preprocessing pipeline, still to come ([roadmap](/roadmap/)).

## History {#history}

- **2026-10-11**: PIPE-03 and SCI-03 corrected by default ([the register](repo:docs/findings/upstream-defects.md)).
- **2026-10-12**: SCI-02's undefined conversions clamped by default, with a warning.
- **2026-10-29**: the version update: the replica follows SciPy 1.18.1 and numpy 2.5.4, kept in a Python environment of their own; SciPy 1.18 fixed SCI-03, and the replica follows its fix in both modes.
