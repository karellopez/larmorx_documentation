---
title: antsRegistration
kicker: Tools · ANTs
lede: Image registration, ported from ANTs 2.6.5 and ITK 5.4.5, with every stage ANTs has — linear, SyN, B-spline SyN, B-spline, displacement-field, exponential and time-varying velocity-field — and every image and point-set metric. Every compared case is identical to ANTs, as built or once ANTs uses correctly rounded maths; on sMRIPrep's own template registration larmorx is ANTs at one thread with correctly rounded maths, on any number of threads.
description: LARMORX's port of antsRegistration, validated against ANTs 2.6.5 — sMRIPrep's T1w-to-MNI registration on real data to inspect (SyN, B-spline SyN, a time-varying velocity field), the displacement fields against ANTs' own thread band, the linear stages' parameters, the corrections LARMORX makes and what they change, and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span> · every stage ANTs has</dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/ants-registration.md') }}">ants-registration</a> (standard tier) · <a href="{{ repo('docs/validation/ants-registration-full.md') }}">full tier</a> (<a href="{{ repo('docs/validation/ants-registration-velocity-full.md') }}">its velocity-field cases</a>) · <a href="{{ repo('docs/validation/ants-registration-corrections.md') }}">the corrections' effects</a> · API <a href="{{ repo('docs/api/ants-registration.md') }}">ants-registration</a></dd>
</dl>

## What it is

antsRegistration aligns a moving image to a fixed one through a sequence of stages, each a transform (rigid, affine, SyN, velocity fields and others) optimised against one or more metrics over a multi-resolution schedule. sMRIPrep uses it for the brain extraction and the registration to the MNI template; fMRIPrep for the BOLD reference and the field-map registration.

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
tvf = lx.ants.RegistrationStage(
    "TimeVaryingVelocityField", 0.5, lx.ants.RegistrationMetric("CC", "fixed.nii.gz", "moving.nii.gz", radius=4),
    iterations=[100, 70, 50, 20], shrink_factors=[8, 4, 2, 1], smoothing_sigmas=[3, 2, 1, 0],
    number_of_time_indices=4, update_field_variance=3.0,
)
res = lx.ants.registration([rigid, tvf], warped=True, random_seed=42)
```

The [API page](repo:docs/api/ants-registration.md) maps every option and stage. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-registration', 'port') }}

Every case that runs is identical to ANTs: exit status, standard output with every iteration's DIAGNOSTIC line, standard error and every file, against the unmodified binary at one thread, or, where glibc's `exp`, `log`, `sin` or `cos` is not correctly rounded for a value the run meets, against the same binary with CORE-MATH's correctly rounded functions preloaded. The rest are inputs both programs refuse and documented divergences (crashes LARMORX refuses with a message, ANTs' samplings seeded from the clock). Nothing is open.

## A worked example: sMRIPrep's template registration {#example}

fMRIPrep's own registration of a T1w to MNI152NLin2009cAsym, run on every third voxel of its images as the record's standard tier runs it (a full-size run takes ANTs about an hour at one thread; the full tier runs it whole). Choose the output: the warped T1w, or one component of the displacement field SyN found. *Checkerboard* and *Swipe* (under *Compare*) set the template against the warped T1w; the difference panels set LARMORX against ANTs as built next to ANTs against itself at 8 threads, on one scale.

{{ ev.example('ants-registration', 'template-syn') }}

{{ ev.example('ants-registration', 'template-bsplinesyn') }}

## A velocity-field registration {#velocity}

The same command with its SyN stage replaced by a time-varying velocity field: the deformation is the flow of a velocity field over space and four time points, integrated from time 0 to 1 by fourth-order Runge–Kutta, and its inverse the flow back. ANTs has no script that sets this stage, so it takes SyN's levels, iterations, metric and smoothing. The exponential stages (a stationary velocity field, its displacement the exponential by scaling and squaring) and the time-varying B-spline field are in the record the same way, on the same images.

{{ ev.example('ants-registration', 'template-tvf') }}

## Against ANTs' own variability {#variability}

ANTs' result moves with its thread count: its metrics sum per-thread partial sums in an order that depends on the threads. The record measures this band and reports, for each case, LARMORX's distance from ANTs at one thread.

{{ ev.dots('ants-registration', 'band') }}

## The corrections, and what they change {#corrections}

LARMORX corrects the defects of the register by default; `upstream_defects="reproduce"` (or `LARMORX_UPSTREAM_DEFECTS=reproduce`) gives ANTs' behaviour, the mode every comparison above runs in. The record's fix pass names, case by case, the corrections a command meets and what they change; none applies to sMRIPrep's commands above. The corrections the user decided on 2026-10-21 change the point-set metrics, the B-spline field meshes and what can follow a B-spline transform; each was measured on phantoms whose answer is known, or against the closest runs ANTs can do ([findings](repo:docs/findings/ants-velocity.md#the-corrections-decided-on-2026-10-21-and-what-they-change)).

{{ ev.table('ants-registration', 'corrections-igdm') }}

{{ ev.table('ants-registration', 'corrections-jhct') }}

{{ ev.table('ants-registration', 'corrections-mesh') }}

ANTs cannot run a stage after a B-spline transform (ITK-35), so the last table sets the corrected stage against the two closest runs ANTs can do: the same stage on the moving image resampled through the B-spline transform, and ANTs given the B-spline transform sampled as a displacement field (at half its control-point spacing) as its initial transform. The field is close for two B-spline stages (a quarter of a millimetre: the field's sampling); for a linear stage it is not, because ITK takes a field's Jacobian from its nearest voxel and the linear stage stops early (LARMORX given the same field stops with it, identically).

{{ ev.table('ants-registration', 'corrections-chain') }}

## Every case {#cases}

Each case of the standard-tier record, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('ants-registration') }}

## Speed {#speed}

No benchmark report yet: the benchmark of antsRegistration is pending ([next steps](repo:docs/next-steps.md)).

## Known limits {#limits}

- MINC transform files are refused with a message.
- The expected divergences: without a seed ANTs seeds its sampling from the clock (LARMORX uses a fixed seed), and so do three of the velocity-field stages whatever the seed (ANTS-82) and a linear stage after a displacement field (ANTS-72); crashes and reads of unwritten memory are not reproduced (ANTS-51, ANTS-66, ANTS-77); messages ANTs prints only with `--verbose` (ANTS-45).
- A stage after a B-spline transform runs in LARMORX (ITK-35, corrected), not in ANTs; give it a mask: the B-spline transform is the identity outside its valid region, so the composite jumps at that border.
- The comparison with ANTs is made on Linux x86-64; the other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md).
