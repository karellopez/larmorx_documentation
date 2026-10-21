---
title: One-shot BOLD resampler
kicker: Tools · fMRIPrep
lede: fMRIPrep's one-shot resampling of a BOLD run (head motion, distortion correction and the registrations in one interpolation), ported with nitransforms' transform chains and SciPy's interpolation. Bit-identical in every compared case; fMRIPrep's Jacobian (PIPE-03) corrected by default.
description: LARMORX's port of fMRIPrep's ResampleSeries, its validation against fMRIPrep, nitransforms and SciPy in figures, PIPE-03's Jacobian on fMRIPrep's own field map, and speed.
---

<dl class="facts">
<dt>Implementation</dt><dd>port of fMRIPrep's <code>ResampleSeries</code>, nitransforms' chains and SciPy's <code>map_coordinates</code>, in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-larmorx">validated</span></dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/resample-series.md') }}">resample-series</a> · <a href="{{ repo('docs/validation/resample-series-jacobian.md') }}">PIPE-03 on real geometry</a> · benchmark <a href="{{ repo('docs/benchmarks/resample-series.md') }}">resample-series</a> · API <a href="{{ repo('docs/api/resample-series.md') }}">resample-series</a></dd>
</dl>

## What it is

fMRIPrep resamples each BOLD volume once, from the original series to every output space: the head-motion transform, the voxel-shift map of the field map along the phase-encoding axis, the registration to the T1w and, for standard spaces, the T1w-to-template warp, composed and applied with cubic B-spline interpolation, with the Jacobian of the distortion correction. Its heaviest computation is this Python code.

## How to call it

```python
import json
import larmorx as lx

meta = json.load(open("sub-01_task-rest_bold.json"))
bold_t1w = lx.transforms.resample_series(
    "sub-01_task-rest_desc-stc_bold.nii.gz",
    "sub-01_space-T1w_boldref.nii.gz",
    ["sub-01_from-orig_to-boldref_mode-image_desc-hmc_xfm.txt",
     "sub-01_from-boldref_to-T1w_mode-image_desc-coreg_xfm.txt"],
    fieldmap="fmap_hz_in_T1w.nii.gz", pe_dir=meta["PhaseEncodingDirection"],
    ro_time=meta["TotalReadoutTime"], jacobian=True, n_threads=8,
)
```

## Agreement with fMRIPrep, nitransforms and SciPy

The [record](repo:docs/validation/resample-series.md) runs 139 cases, in-process against fMRIPrep's `ResampleSeries`, nitransforms 25.1.0 and SciPy 1.15: 136 pass, every one bit-identical to its reference (with `upstream_defects="reproduce"`), 2 are rejected by both and 1 is an expected divergence (coordinates beyond the range of 64-bit integers, where SciPy's C code is undefined).

{{ figure('resample-series/agreement', "The record's 139 cases by category: bit-identical to the reference, the expected divergence and the inputs both refuse.") }}

## PIPE-03: the Jacobian on fMRIPrep's own field map

fMRIPrep multiplies the distortion-corrected BOLD by one plus the gradient of the voxel-shift map along the target grid's axis that has the source's phase-encoding index, in target voxels. That is the Jacobian only on the BOLD's own grid; on T1w and template grids it is taken along another direction and in other units ([register](repo:docs/findings/upstream-defects.md), PIPE-03). LARMORX differentiates along the phase-encoding direction mapped into the target grid, by default. On fMRIPrep's own field maps the [record](repo:docs/validation/resample-series-jacobian.md) measures both against the factor on the BOLD's own grid, where the two agree bit for bit: on ds005040's MNI grid, fMRIPrep's factor errs by 0.0124 at the median and 0.101 at the 99th percentile, LARMORX's by 0.0051 and 0.063.

{{ figure('resample-series/jacobian', "OpenNeuro ds005040 sub-002 (CC0-1.0), its PEPOLAR field map as fMRIPrep 25.2.6 estimated it, on the MNI152NLin2009cAsym 2 mm grid; axial slices inside fMRIPrep's brain mask. Top: the Jacobian factor as fMRIPrep computes it, as LARMORX computes it by default, and the reference (the factor on the BOLD's own grid carried to this grid). Bottom: each factor's error against the reference, on one symmetric scale (the 99.5th percentile of both). The template: MNI ICBM 152 nonlinear asymmetric 2009c, © McConnell Brain Imaging Centre, Montreal Neurological Institute ([notice](/static/hero/LICENSE-MNI.txt)).") }}

## Speed

{{ figure('resample-series/speed', "Median seconds of the resampling (as `ResampleSeries` runs it, without the file I/O) for fMRIPrep's code and LARMORX at 1 and 12 threads, on real BOLD runs with seeded head motion and field maps, from the benchmark report of 2026-10-10 (Intel i7-8750H, 12 logical CPUs); the factor is LARMORX's speed-up at one thread.") }}

## Corrections by default

PIPE-03 (fMRIPrep's Jacobian) and SCI-03 (SciPy's `reflect` and `grid-mirror` splines on short axes) are corrected by default; `upstream_defects="reproduce"` gives fMRIPrep's and SciPy's results bit for bit ([register](repo:docs/findings/upstream-defects.md)). A report of PIPE-03 for fMRIPrep is drafted, not yet filed.

## Known limits

The resampler covers fMRIPrep's one-shot path; the field-map estimation itself (sdcflows) is planned.
