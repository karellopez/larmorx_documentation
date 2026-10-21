---
title: antsRegistration
kicker: Tools · ANTs
lede: Image registration, ported from ANTs 2.6.5 and ITK 5.4.5, with its linear, SyN, B-spline SyN, B-spline and displacement-field stages and every image and point-set metric. Every compared case is identical to ANTs, as built or once ANTs uses correctly rounded maths; on sMRIPrep's own template registration larmorx is ANTs at one thread with correctly rounded maths, on any number of threads.
description: LARMORX's port of antsRegistration, validated against ANTs 2.6.5 — sMRIPrep's T1w-to-MNI registration on real data to inspect (SyN and B-spline SyN), the displacement fields against ANTs' own thread band, the linear stages' parameters, and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span> · the velocity-field and exponential stages are planned</dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/ants-registration.md') }}">ants-registration</a> (standard tier) · <a href="{{ repo('docs/validation/ants-registration-full.md') }}">full tier</a> · API <a href="{{ repo('docs/api/ants-registration.md') }}">ants-registration</a></dd>
</dl>

## What it is

antsRegistration aligns a moving image to a fixed one through a sequence of stages, each a transform (rigid, affine, SyN and others) optimised against one or more metrics over a multi-resolution schedule. sMRIPrep uses it for the brain extraction and the registration to the MNI template; fMRIPrep for the BOLD reference and the field-map registration.

```bash
larmorx ants antsRegistration -d 3 -o [t1_to_mni_,t1_to_mni_Warped.nii.gz] \
  -t Rigid[0.05] -m Mattes[mni.nii.gz,t1w.nii.gz,1,56,Regular,0.25] -c [100x100,1e-6,20] -f 2x1 -s 2x1vox \
  -t SyN[0.1,3,0] -m CC[mni.nii.gz,t1w.nii.gz,1,4] -c [100x70x50x20,1e-6,10] -f 8x4x2x1 -s 3x2x1x0vox
```

```python
import larmorx as lx

rigid = lx.ants.RegistrationStage(
    transform="Rigid", gradient_step=0.1,
    metrics=lx.ants.RegistrationMetric("Mattes", "fixed.nii.gz", "moving.nii.gz",
                                       bins=32, sampling="Regular", sampling_percentage=0.25),
    iterations=[1000, 500, 250], shrink_factors=[4, 2, 1], smoothing_sigmas=[2, 1, 0],
)
res = lx.ants.registration([rigid], warped=True, random_seed=42)
```

The [API page](repo:docs/api/ants-registration.md) maps every option and stage. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-registration', 'port') }}

Every case that runs is identical to ANTs: exit status, standard output with every iteration's DIAGNOSTIC line, standard error and every file, against the unmodified binary at one thread, or, where glibc's `exp`, `log`, `sin` or `cos` is not correctly rounded for a value the run meets, against the same binary with CORE-MATH's correctly rounded functions preloaded. The rest are inputs both programs refuse and documented divergences (crashes LARMORX refuses with a message, a clock-seeded sampling, the planned velocity-field stages). Nothing is open.

## A worked example: sMRIPrep's template registration {#example}

fMRIPrep's own registration of a T1w to MNI152NLin2009cAsym, run on every third voxel of its images as the record's standard tier runs it (a full-size run takes ANTs about an hour at one thread; the full tier runs it whole). Choose the output: the warped T1w, or one component of the displacement field SyN found. *Checkerboard* and *Swipe* (under *Compare*) set the template against the warped T1w; the difference panels set LARMORX against ANTs as built next to ANTs against itself at 8 threads, on one scale.

{{ ev.example('ants-registration', 'template-syn') }}

{{ ev.example('ants-registration', 'template-bsplinesyn') }}

## Against ANTs' own variability {#variability}

ANTs' result moves with its thread count: its metrics add per-thread partial sums in an order that depends on the threads. The record measures this band on 30 cases and reports, for each, LARMORX's distance from ANTs at one thread.

{{ ev.dots('ants-registration', 'band') }}

## Every case {#cases}

Each case of the standard-tier record, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('ants-registration') }}

## Speed {#speed}

No benchmark report yet: the benchmark of antsRegistration is pending ([next steps](repo:docs/next-steps.md)).

## Corrections by default {#corrections}

The record's fix pass meets ANTS-49, ANTS-61, ANTS-62, ANTS-63, ANTS-65, ANTS-73, ANTS-76, ITK-18, ITK-22, ITK-23, ITK-26, ITK-30, ITK-31, ITK-32 and ITK-33: each corrected by default, with `upstream_defects="reproduce"` (or `LARMORX_UPSTREAM_DEFECTS=reproduce`) giving ANTs' behaviour, the mode the comparison runs in ([register](repo:docs/findings/upstream-defects.md)). None of them applies to sMRIPrep's command above: both modes give the same bytes. ANTS-78, ITK-35 and five point-set defects are to be corrected with the next part.

## Known limits {#limits}

- The time-varying velocity-field and exponential stages are not ported yet; LARMORX refuses them with a message.
- `antsApplyTransforms` does not read `BSplineTransform` files yet (`warped=True` gives the warped image).
- The expected divergences: without a seed ANTs seeds its sampling from the clock (LARMORX uses a fixed seed); crashes and reads of unwritten memory are not reproduced (ANTS-51, ANTS-66, ANTS-77); messages ANTs prints only with `--verbose` (ANTS-45); MINC transform files are refused; a linear stage after a displacement field draws its voxels from a clock-seeded generator in ANTs (ANTS-72).
- The comparison with ANTs is made on Linux x86-64; the other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md).
