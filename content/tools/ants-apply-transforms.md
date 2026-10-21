---
title: antsApplyTransforms
kicker: Tools · ANTs
lede: Resampling an image through a chain of ITK transforms, ported from ANTs 2.6.5 and ITK 5.4.5, in double precision and with --float 1, and the transform outputs. Bit-identical to ANTs in every compared case once ANTs uses correctly rounded maths.
description: LARMORX's port of antsApplyTransforms, its validation against ANTs 2.6.5 in figures, fMRIPrep's T1w-to-MNI transform applied by both, and speed.
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/ants-apply-transforms.md') }}">ants-apply-transforms</a> · benchmark <a href="{{ repo('docs/benchmarks/ants-apply-transforms.md') }}">ants-apply-transforms</a> · API <a href="{{ repo('docs/api/ants-apply-transforms.md') }}">ants-apply-transforms</a></dd>
</dl>

## What it is

antsApplyTransforms maps every voxel of a reference grid through a list of transforms (matrices, displacement fields, composite `.h5` files) into an input image and interpolates it there: linear, nearest neighbour, B-spline, Gaussian, windowed sinc, label-preserving. fMRIPrep uses it for every resampling of its anatomical outputs and masks, many of them with `--float 1`.

## How to call it

```bash
larmorx ants antsApplyTransforms -d 3 -i sub-01_desc-preproc_T1w.nii.gz -r tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz \
  -t sub-01_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5 -n LanczosWindowedSinc -o t1w_mni.nii.gz
```

```python
import larmorx as lx

mni = lx.ants.apply_transforms(
    "sub-01_desc-preproc_T1w.nii.gz",
    "tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz",
    ["sub-01_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5"],
    interpolation="lanczos", n_threads=8,
)
```

## Agreement with ANTs

The [record](repo:docs/validation/ants-apply-transforms.md) runs 220 cases: 202 pass, 14 are rejected by both programs and 4 are expected divergences. Against the unmodified binary, 160 of the 174 passing cases with an image output are bit-identical; the other 14 differ only through glibc's `exp`, `log`, `sin`, `cos` and their float versions (Gaussian and windowed-sinc weights, Euler and versor matrices), and with CORE-MATH preloaded into ANTs all 174 are. All 89 `--float 1` cases are bit-identical to the unmodified binary. The 28 cases that write transforms write ANTs' files: text and MATLAB files byte for byte, NIfTI displacement fields bit for bit, HDF5 files dataset for dataset (byte for byte given ITK's compressed chunks).

{{ figure('ants-apply-transforms/agreement', "The record's 220 cases by category: image outputs identical to ANTs as built or identical with CORE-MATH, transform files with ANTs' content, expected divergences (crashes of ANTs that LARMORX refuses with a message) and the inputs both programs refuse.") }}

## fMRIPrep's T1w-to-MNI transform

{{ figure('ants-apply-transforms/t1w-to-mni', "fMRIPrep 25.2.6's T1w-to-MNI152NLin2009cAsym composite (affine and SyN warp, `.h5`) applied to OpenNeuro ds000005 sub-01's preprocessed T1w (PDDL-1.0) with Lanczos interpolation, on the template's 2 mm grid; axial slices inside the template's brain mask. In double precision LARMORX differs from ANTs as built in scattered voxels, by at most 7 × 10⁻¹³ (glibc's `sin` and `cos` in the Lanczos weights); with `--float 1`, and with CORE-MATH preloaded into ANTs, the outputs are bit-identical. The template: MNI ICBM 152 nonlinear asymmetric 2009c, © McConnell Brain Imaging Centre, Montreal Neurological Institute ([notice](/static/hero/LICENSE-MNI.txt)).") }}

## Speed

{{ figure('ants-apply-transforms/speed', "Median seconds of the whole command (reading, resampling, writing) for antsApplyTransforms (ANTs 2.6.5 through ANTsPy) and LARMORX's command line at 1 and 12 threads on fMRIPrep's resampling jobs, from the benchmark report of 2026-10-10 (Intel i7-8750H, 12 logical CPUs); the factor is LARMORX's speed-up at one thread.") }}

The report predates `--float 1`; a re-run is among the planned follow-ups ([next steps](repo:docs/next-steps.md)).

## Corrections by default

The record's fix pass meets ANTS-06 (undefined float-to-integer conversions of `-u char`/`uchar` outputs, clamped by default; [register](repo:docs/findings/upstream-defects.md)).

## Known limits

`BSplineTransform` files (the output of antsRegistration's `BSpline` stage) are refused with a message; MINC transform files too.
