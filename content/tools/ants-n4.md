---
title: N4BiasFieldCorrection
kicker: Tools · ANTs
lede: Intensity non-uniformity correction, ported from ANTs 2.6.5 and ITK 5.4.5. Every case of its record is bit-identical to ANTs, as built or once ANTs uses correctly rounded maths; on fMRIPrep's own N4 of a real T1w, larmorx is ANTs at one thread with correctly rounded maths, at any thread count.
description: LARMORX's port of ANTs' N4BiasFieldCorrection, validated against ANTs 2.6.5 and fMRIPrep 25.2.6 — a worked example on a real T1w to inspect, every parity case with its verdict, ANTs' own variability, and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/ants-n4.md') }}">ants-n4</a> · benchmark <a href="{{ repo('docs/benchmarks/ants-n4.md') }}">ants-n4</a> · API <a href="{{ repo('docs/api/ants-n4.md') }}">ants-n4</a> · findings <a href="{{ repo('docs/findings/ants-n4.md') }}">ants-n4</a></dd>
</dl>

## What it is

N4 estimates a smooth multiplicative bias field by fitting B-splines to the residual of a sharpened intensity histogram, level by level, and divides it out. fMRIPrep, sMRIPrep and sdcflows call it on BOLD references, T1w images (before the template and in the brain extraction) and field-map magnitudes.

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

The [API page](repo:docs/api/ants-n4.md) maps every option. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-n4', 'port') }}

Every case that produces an image is bit-identical to ANTs: as built (glibc's maths, one thread), or, where glibc's `expf`, `logf`, `exp` or `sincos` is not correctly rounded for a value the run meets, once the same ANTs binary uses CORE-MATH's correctly rounded functions. The invalid inputs are refused by both programs. Nothing is open.

## A worked example: fMRIPrep's own N4 {#example}

The image viewer below holds the same N4 run by fMRIPrep 25.2.6, by its own ANTs at one thread, by the repository's ANTs 2.6.5 (as built, with correctly rounded maths, at 1 to 12 threads) and by larmorx (1 and 12 threads, default and reproduce modes). Choose the panels, the plane, the slice and the window; select a point to read every panel's exact value there; set two images side by side, swipe or blink between them.

{{ ev.example('ants-n4', 'final-n4') }}

## Against ANTs' own variability {#variability}

ANTs' N4 changes with its thread count ([ANTS-37](repo:docs/findings/upstream-defects.md)): ITK's B-spline fit sums per-thread lattices. The record measures that band for every case that differs from ANTs as built, and divides larmorx's difference by it.

{{ ev.band('ants-n4') }}

## Every case {#cases}

Each case of the record, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('ants-n4') }}

## Speed {#speed}

{{ ev.speed('ants-n4') }}

## Corrections by default {#corrections}

Where ANTs has a deterministic defect that changes a result, LARMORX corrects it by default and warns; `upstream_defects="reproduce"` (or `LARMORX_UPSTREAM_DEFECTS=reproduce`) gives ANTs' behaviour, and the record compares in that mode. Its fix pass meets ANTS-35, ANTS-36, ANTS-38 and ITK-02 ([register](repo:docs/findings/upstream-defects.md), [findings](repo:docs/findings/ants-n4.md)); none of them applies to fMRIPrep's command above, so both modes give the same bytes there.

## Known limits {#limits}

The comparison with ANTs is made on Linux x86-64; the other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). ANTs' oracle is built by GCC 14.3, which honours the source's float roundings; an older GCC 11 build of ANTs gives other bits ([findings](repo:docs/findings/ants-n4.md)).
