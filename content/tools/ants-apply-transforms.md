---
title: antsApplyTransforms
kicker: Tools · ANTs
lede: Resampling an image through a chain of ITK transforms, ported from ANTs 2.6.5 and ITK 5.4.5, in double precision and with --float 1, and the transform outputs. Every compared case is identical to ANTs, as built or once ANTs uses correctly rounded maths; fMRIPrep's own T1w-to-MNI resampling is bit-identical.
description: LARMORX's port of antsApplyTransforms, validated against ANTs 2.6.5 and fMRIPrep 25.2.6 — fMRIPrep's T1w-to-MNI resampling through its .h5 composite to inspect, in single and double precision, every parity case with its verdict, and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/ants-apply-transforms.md') }}">ants-apply-transforms</a> · benchmark <a href="{{ repo('docs/benchmarks/ants-apply-transforms.md') }}">ants-apply-transforms</a> · API <a href="{{ repo('docs/api/ants-apply-transforms.md') }}">ants-apply-transforms</a></dd>
</dl>

## What it is

antsApplyTransforms maps every voxel of a reference grid through a list of transforms (matrices, displacement fields, composite `.h5` files) into an input image and interpolates it there: linear, nearest neighbour, B-spline, Gaussian, windowed sinc, label-preserving. fMRIPrep uses it for every resampling of its anatomical outputs and masks, many of them with `--float 1`.

```bash
larmorx ants antsApplyTransforms -d 3 --float 1 -i sub-01_desc-preproc_T1w.nii.gz -r tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz \
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

How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-apply-transforms', 'port') }}

Image outputs are bit-identical to the unmodified ANTs binary, or, where glibc's `exp`, `sin` or `cos` is not correctly rounded (Gaussian and windowed-sinc weights, Euler and versor matrices), to the same binary with CORE-MATH preloaded. Every `--float 1` case is bit-identical to ANTs as built. The cases that write transforms (`-o Linear[...]`, `CompositeTransform[...]`, `DisplacementField[...]`) write ANTs' content: text and MATLAB files byte for byte, NIfTI fields bit for bit, HDF5 files dataset for dataset and attribute for attribute (their compressed bytes are ITK's given ITK's chunks). The expected divergences are crashes of ANTs that LARMORX refuses with a message.

## A worked example: fMRIPrep's T1w in MNI space {#example}

The node that writes fMRIPrep's `space-MNI152NLin2009cAsym_res-2_desc-preproc_T1w`: its masked T1w, the 2 mm template and its own composite transform (the affine and the SyN displacement field of its template registration), with Lanczos interpolation. fMRIPrep runs it with `--float 1`; double precision is shown beside it, where glibc's maths reaches the last bits.

{{ ev.example('ants-apply-transforms', 'fmriprep-anat2std') }}

## Every case {#cases}

Each case of the record, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('ants-apply-transforms') }}

## Speed {#speed}

{{ ev.speed('ants-apply-transforms') }}

## Corrections by default {#corrections}

The record's fix pass meets ANTS-06 (undefined float-to-integer conversions of `-u char`/`uchar` outputs, clamped by default; [register](repo:docs/findings/upstream-defects.md)); it does not apply to fMRIPrep's commands.

## Known limits {#limits}

`BSplineTransform` files (the output of antsRegistration's `BSpline` stage) are refused with a message; MINC transform files too. The comparison is made on Linux x86-64; the other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md).
