---
title: antsRegistration
kicker: Tools · ANTs
lede: Image registration, ported from ANTs 2.6.5 and ITK 5.4.5, with its linear, SyN, B-spline SyN, B-spline and displacement-field stages and every image and point-set metric. Identical to ANTs in every compared case, once ANTs uses correctly rounded maths.
description: LARMORX's port of antsRegistration, its validation against ANTs 2.6.5 in figures, ANTs' own thread variability, and sMRIPrep's template registration by ANTs and LARMORX.
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span> · the velocity-field and exponential stages are planned</dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/ants-registration.md') }}">ants-registration</a> (standard tier) · <a href="{{ repo('docs/validation/ants-registration-full.md') }}">full tier</a> · API <a href="{{ repo('docs/api/ants-registration.md') }}">ants-registration</a></dd>
</dl>

## What it is

antsRegistration aligns a moving image to a fixed one through a sequence of stages, each a transform (rigid, affine, SyN and others) optimised against one or more metrics over a multi-resolution schedule. sMRIPrep uses it for the brain extraction and the registration to the MNI template; fMRIPrep for the BOLD reference and the field-map registration.

## How to call it

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
res.files["0GenericAffine.mat"]
```

LARMORX gives ANTs' one-thread result at any thread count. The [API page](repo:docs/api/ants-registration.md) maps every option and stage.

## Agreement with ANTs

The [standard-tier record](repo:docs/validation/ants-registration.md) runs 403 cases with ANTs at one thread and `ANTS_RANDOM_SEED=42`: 309 pass, 77 are rejected by both programs (exit status and messages compared) and 17 are expected divergences, with no failure. Of the 309 compared cases, 273 are identical to the unmodified ANTs (exit status, standard output with every diagnostic line, standard error, every file) and 36 once ANTs uses CORE-MATH's correctly rounded `exp`, `log`, `sin` and `cos`. The [full tier](repo:docs/validation/ants-registration-full.md) adds sMRIPrep's whole brain extractions and template registrations on the five oracle runs: 441 cases, 346 compared, 278 and 68 identical, no failure.

{{ figure('ants-registration/agreement', "The standard tier's 403 cases by category. The first bar splits the compared cases between identical to ANTs as built and identical with CORE-MATH, as the record states them; the categories' bars show their compared cases together.") }}

## ANTs' own variability

ANTs' result changes with its thread count. The record measures it on 30 cases: from nothing to about 10⁻¹² for most metrics, and up to 1.87 in a transform parameter for sMRIPrep's deformable registrations on real images.

{{ figure('ants-registration/thread-band', "For each of the 30 cases measured, the largest change in a transform parameter between ANTs at one thread and ANTs at 2, 4 and 8 threads (log scale), from the record's thread-band sentence; the cases the threads leave unchanged are listed above.") }}

## sMRIPrep's template registration

{{ figure('ants-registration/template-registration', "fMRIPrep 25.2.6's registration of OpenNeuro ds000005 sub-01's T1w (PDDL-1.0) to MNI152NLin2009cAsym (Rigid, Affine, SyN), on every third voxel of its images as in the record's `real-syn-small` case; axial slices in template space. Top: the template with the contour of LARMORX's warped T1w, a checkerboard of the two, the warped T1w. Bottom: the magnitude of the difference between displacement fields, in mm on one scale: LARMORX against ANTs as built (both at their one-thread result), ANTs at four threads against one, and LARMORX against ANTs with CORE-MATH. glibc's maths moves ANTs' SyN field by about as much as its own threads do; with correctly rounded maths the two are bit-identical. The template: MNI ICBM 152 nonlinear asymmetric 2009c, © McConnell Brain Imaging Centre, Montreal Neurological Institute ([notice](/static/hero/LICENSE-MNI.txt)).") }}

## Speed

No benchmark report yet: the benchmark of antsRegistration is pending ([next steps](repo:docs/next-steps.md)).

## Corrections by default

The record's fix pass meets ANTS-49, ANTS-61, ANTS-62, ANTS-63, ANTS-65, ANTS-73, ANTS-76, ITK-18, ITK-22, ITK-23, ITK-26, ITK-30, ITK-31, ITK-32 and ITK-33: each corrected by default, with `upstream_defects="reproduce"` (or `LARMORX_UPSTREAM_DEFECTS=reproduce`) giving ANTs' behaviour, the mode the comparison runs in ([register](repo:docs/findings/upstream-defects.md)). ANTS-78, ITK-35 and five point-set defects are to be corrected with the next part.

## Known limits

- The time-varying velocity-field and exponential stages are not ported yet; LARMORX refuses them with a message.
- `antsApplyTransforms` does not read `BSplineTransform` files yet (`warped=True` gives the warped image).
- The expected divergences: without a seed ANTs seeds its sampling from the clock (LARMORX uses a fixed seed); crashes and reads of unwritten memory are not reproduced (ANTS-51, ANTS-66, ANTS-77); messages ANTs prints only with `--verbose` (ANTS-45); MINC transform files are refused; a linear stage after a displacement field draws its voxels from a clock-seeded generator in ANTs (ANTS-72).
