---
title: N4BiasFieldCorrection
kicker: Tools · ANTs
lede: Intensity non-uniformity correction, ported from ANTs 2.6.5 and ITK 5.4.5. Bit-identical to ANTs in every compared case once ANTs uses correctly rounded maths.
description: LARMORX's port of ANTs' N4BiasFieldCorrection, its validation against ANTs 2.6.5 in figures, a bias field on a real T1w, and its speed.
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/ants-n4.md') }}">ants-n4</a> · benchmark <a href="{{ repo('docs/benchmarks/ants-n4.md') }}">ants-n4</a> · API <a href="{{ repo('docs/api/ants-n4.md') }}">ants-n4</a></dd>
</dl>

## What it is

N4 estimates a smooth multiplicative bias field by fitting B-splines to the residual of a sharpened intensity histogram, level by level, and divides it out. fMRIPrep, sMRIPrep and sdcflows call it on BOLD references, T1w images (before the template, in the brain extraction) and field-map magnitudes.

## How to call it

```bash
larmorx ants N4BiasFieldCorrection -d 3 -b [200] -c [50x50x50x50x50,1e-7] -s 4 -i t1w.nii.gz -o [t1w_n4.nii.gz,bias.nii.gz]
```

```python
import larmorx as lx

res = lx.ants.n4_bias_field_correction(
    "sub-01_T1w.nii.gz", shrink_factor=4,
    convergence=([50] * 5, 1e-7), bspline_fitting=200, n_threads=8,
)
corrected, bias = res.corrected, res.bias_field
```

LARMORX computes ANTs' single-thread result on any number of threads. The [API page](repo:docs/api/ants-n4.md) maps every option.

## Agreement with ANTs

The [record](repo:docs/validation/ants-n4.md) runs 51 cases (the standard tier): fMRIPrep's, sMRIPrep's and sdcflows' own command lines on real images, every option, inputs of every kind and the error cases. 46 pass and 5 are rejected by both programs. Against the unmodified ANTs binary (one thread), 29 of the 45 compared cases are bit-identical; the others differ where glibc's `expf`, `logf`, `exp` or `sincos` is not correctly rounded for a value the run meets. With those functions replaced by CORE-MATH's in the same ANTs binary, 45 of 45 are bit-identical.

{{ figure('ants-n4/agreement', "The record's 51 cases by category (the standard tier): identical to ANTs as built, identical once ANTs uses correctly rounded maths, `--help` (no image to compare) and the inputs both programs refuse. Drawn from `docs/validation/ants-n4.json` and `.md`.") }}

## Against ANTs' own variability

ANTs' N4 changes with its thread count. For each case that differs from ANTs as built, the record divides LARMORX's difference by ANTs' own difference between one thread and 2, 3, 4, 8 and 12 threads. Most ratios lie below 1, inside ANTs' variability; three values exceed it, in two cases (`fmriprep/smriprep-pre-template` and `options/shrink-3`, by up to 4.2 for one minus the correlation). All of these differences vanish with correctly rounded maths.

{{ figure('ants-n4/band', "Each differing case's largest difference and one minus its correlation with ANTs as built, divided by ANTs' thread band, on a log scale; the 29 bit-identical cases are counted at the left. From the record's table of these differences.") }}

## On a real T1w

{{ figure('ants-n4/bias-field', "OpenNeuro ds000005 sub-01's T1w (PDDL-1.0) with sMRIPrep's final N4 options without a weight image (`-b [200] -c [50x50x50x50x50,1e-07] -s 4`), axial slices inside fMRIPrep's brain mask: the input, LARMORX's bias field and corrected image; then the corrected image's differences on one symmetric scale: LARMORX against ANTs as built at one thread, ANTs at four threads against one, and LARMORX against ANTs with CORE-MATH. On this image LARMORX's output is bit-identical to ANTs' (every voxel), while ANTs' own result moves with its threads.") }}

## Speed

{{ figure('ants-n4/speed', "Median seconds of the whole command (reading, N4, writing) for ANTs 2.6.5 and LARMORX at 1 and 12 threads on the pipelines' calls, from the benchmark report of 2026-10-11 (Intel i7-8750H, 12 logical CPUs); the factor is LARMORX's speed-up at one thread.") }}

A re-run against the current oracle build is among the planned follow-ups ([next steps](repo:docs/next-steps.md)).

## Corrections by default

Where ANTs has a deterministic defect that changes a result, LARMORX corrects it by default and warns; `upstream_defects="reproduce"` (or `LARMORX_UPSTREAM_DEFECTS=reproduce`) gives ANTs' behaviour, and the record compares in that mode. Its fix pass meets ANTS-35, ANTS-36, ANTS-38 and ITK-02 ([register](repo:docs/findings/upstream-defects.md), [findings](repo:docs/findings/ants-n4.md)).

## Known limits

The comparison with ANTs is made on Linux x86-64; the other five platforms are held to LARMORX's own Linux output by the golden tests. ANTs' oracle is built by GCC 14.3, which honours the source's float roundings; an older GCC 11 build of ANTs gives other bits ([findings](repo:docs/findings/ants-n4.md)).
