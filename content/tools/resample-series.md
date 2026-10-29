---
title: One-shot BOLD resampler
kicker: Tools · fMRIPrep
lede: fMRIPrep's one-shot resampling of a BOLD run (head motion, distortion correction and the registrations in one interpolation), ported with nitransforms' transform chains and SciPy's interpolation, following SciPy 1.18.1 and numpy 2.5.4 since 2026-10-29. Bit-identical in every compared case and on fMRIPrep's own run with its field map; fMRIPrep's Jacobian on other grids (PIPE-03) corrected by default.
description: LARMORX's port of fMRIPrep's ResampleSeries, validated against fMRIPrep 25.2.6, nitransforms, SciPy 1.18.1 and numpy 2.5.4 (with the step from SciPy 1.15.3 and numpy 2.3.5) — fMRIPrep's resampling of a real run with its field map to inspect, PIPE-03's Jacobian against the reference, every parity case with its verdict, and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>port of fMRIPrep's <code>ResampleSeries</code>, nitransforms' chains and SciPy's <code>map_coordinates</code>, in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-larmorx">validated</span></dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/resample-series.md') }}">resample-series</a> · <a href="{{ repo('docs/validation/resample-series-jacobian.md') }}">PIPE-03 on real geometry</a> · benchmark <a href="{{ repo('docs/benchmarks/resample-series.md') }}">resample-series</a> · API <a href="{{ repo('docs/api/resample-series.md') }}">resample-series</a></dd>
</dl>

## What it is

fMRIPrep resamples each BOLD volume once, from the original series to every output space: the head-motion transform, the voxel-shift map of the field map along the phase-encoding axis, the registration to the T1w and, for standard spaces, the T1w-to-template warp, composed and applied with cubic B-spline interpolation, with the Jacobian of the distortion correction. Its heaviest computation is this Python code.

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

How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('resample-series', 'port') }}

The [record](repo:docs/validation/resample-series.md) runs its cases in-process against fMRIPrep's `ResampleSeries`, nitransforms and SciPy, with `upstream_defects="reproduce"`: every compared case is bit-identical to its reference. The expected divergence is a case of coordinates beyond the range of 64-bit integers, where SciPy's C code is undefined.

Since the version update of 2026-10-29 the record runs against the newest releases, SciPy 1.18.1 and numpy 2.5.4 with OpenBLAS 0.3.34, kept in a Python environment of their own beside the one the other suites share (SciPy 1.15.3, numpy 2.3.5). Each case also runs its reference under the older releases and says what changed between them, and why: 122 of 136 compared cases give the same values; 14 change, every one through SciPy's own fix of the `reflect` boundary (SCI-03, [below](#corrections)): `map_coordinates` and the spline filters in modes `reflect`, `grid-mirror` and `nearest`, orders 2 to 5, where LARMORX follows SciPy 1.18.1. numpy's new release changes nothing LARMORX follows (its 4 × 4 products and inverses, checked on 18 million results).

## A worked example: fMRIPrep's resampling with a field map {#example}

fMRIPrep's resampler also ran here on the node's inputs, once with the newest releases and once with the shared environment's (a panel each): on this call (mode `grid-constant`) the two give the same values, every one, and LARMORX's output is theirs.

{{ ev.example('resample-series', 'fmriprep-native') }}

## PIPE-03: the Jacobian on another grid {#pipe-03}

On the BOLD's own grid, above, fMRIPrep's Jacobian is the right factor and both modes give the same bytes. fMRIPrep resamples the same run onto T1w and template grids in the same step, and there it differentiates the voxel-shift map along the wrong axis and in the wrong units ([register](repo:docs/findings/upstream-defects.md), PIPE-03). LARMORX takes the derivative along the BOLD's phase-encoding axis, in its voxels, by default; the [record](repo:docs/validation/resample-series-jacobian.md) measures both factors against the exact one on every grid of three oracle runs.

{{ ev.example('resample-series', 'pipe-03') }}

## Every case {#cases}

Each case of the record, with what it tests, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('resample-series') }}

## Speed {#speed}

{{ ev.speed('resample-series') }}

## Corrections by default {#corrections}

PIPE-03 (fMRIPrep's Jacobian) is corrected by default; `upstream_defects="reproduce"` gives fMRIPrep's result bit for bit ([register](repo:docs/findings/upstream-defects.md)). SCI-03 (SciPy's `reflect`, `grid-mirror` and `nearest` splines missing the samples on short axes, up to SciPy 1.17) was corrected by default from 2026-10-11; SciPy 1.18 fixed it, and LARMORX follows SciPy 1.18.1's fix in both modes since 2026-10-29. A report of PIPE-03 for fMRIPrep is drafted, not yet filed.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/resample-series/') }}

## Known limits {#limits}

The resampler covers fMRIPrep's one-shot path; the field-map estimation itself (sdcflows) is planned.
