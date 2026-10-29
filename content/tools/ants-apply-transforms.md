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
<dt>Data panel</dt><dd><a href="{{ repo('docs/validation/ants-apply-transforms-panel.md') }}">ants-apply-transforms-panel</a></dd>
</dl>

## What it is

antsApplyTransforms maps every voxel of a reference grid through a list of transforms (matrices, displacement fields, B-spline transforms, composite `.h5` files) into an input image and interpolates it there: linear, nearest neighbour, B-spline, Gaussian, windowed sinc, label-preserving. fMRIPrep uses it for every resampling of its anatomical outputs and masks, many of them with `--float 1`.

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

## A B-spline transform {#bspline}

The output of antsRegistration's `BSpline` stage: a cubic B-spline transform, here the one ANTs 2.6.5 found for the same T1w (sMRIPrep's template registration with `BSpline[0.1,104]` in place of its SyN stage, on every third voxel), applied with the registration's affine to the 1 mm T1w onto the 2 mm template, Lanczos, in single and double precision. *Swipe* sets the T1w through the affine alone against it through the B-spline transform too.

Why 104 mm and not antsRegistrationSyN.sh's 26 mm: the mesh doubles at each level, to about a million parameters at the last one, and ANTs computes every parameter's Jacobian at every voxel. With 26 mm ANTs had not finished after almost four hours at 4 threads; LARMORX, which computes only the 64 control points around each voxel, ran the same registration in 38 s at one thread ([findings](repo:docs/findings/ants-bspline.md)).

{{ ev.example('ants-apply-transforms', 'bspline-transform') }}

## On the data panel {#data-panel}

The [data panel](/data-panel/) is the fixed set of fourteen OpenNeuro subjects every tool of LARMORX is validated on: 1.5, 3 and 7 T; Siemens, GE and Philips; single-band, multiband and multi-echo BOLD; a 3.5-year-old to an 82-year-old; a tumour, a stroke with its lesion mask, strong motion. Each record of the panel tier replays every call fMRIPrep 25.2.6 made of the program in its fourteen oracle runs, the node's own `command.txt` with its inputs from the run's working directory (calls repeated word for word are compared once), and runs the program on panel images fMRIPrep never gives it. ANTs runs at one thread, as built and with correctly rounded maths, and at 2 and 3 threads for its own variability where it has any; LARMORX in reproduce mode, and in its default mode for the corrections. The panel's cases are in the case explorers below (categories `panel-fmriprep` and `panel-images`).

**425 of 425 bit-identical to ANTs with correctly rounded maths, 329 to ANTs as built**: every antsApplyTransforms node of the fourteen runs (421 calls; 179 through fMRIPrep's `.h5` composites, 166 with `--float 1`; Gaussian, MultiLabel, windowed sinc, linear and nearest-neighbour interpolation) and four calls fMRIPrep never makes (the 600-volume multiband-8 series onto the T1w, the raw 7 T MP2RAGE and the stroke's lesion mask to MNI, the 82-year-old's FLAIR onto its T1w). The others differ only where ITK calls glibc's `exp`, `log`, `sin` or `cos`.

{{ ev.table('ants-apply-transforms', 'panel-nodes') }}

Images on a small grid (a BOLD reference, a template at 2 mm) are shown as whole volumes; the panel's large anatomical images (up to 17.5 million voxels) as three full-resolution slices through the voxel where LARMORX and ANTs as built differ most (the centre of the field of view where they agree), the whole field of view shown, defaced heads included (the data panel's defacing check).

{{ ev.example('ants-apply-transforms', 'panel-7t-to-mni') }}

{{ ev.example('ants-apply-transforms', 'panel-lesion-to-mni') }}

{{ ev.example('ants-apply-transforms', 'panel-flair-to-t1w') }}

## Every case {#cases}

Each case of the record, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('ants-apply-transforms') }}

## Speed {#speed}

{{ ev.speed('ants-apply-transforms') }}

## Corrections by default {#corrections}

The record's fix pass meets ANTS-06 (undefined float-to-integer conversions of `-u char`/`uchar` outputs, clamped by default; [register](repo:docs/findings/upstream-defects.md)); it does not apply to fMRIPrep's commands.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/ants-apply-transforms/') }}

## Known limits {#limits}

MINC transform files are refused with a message. A B-spline transform has no inverse: `-t [BSpline.txt,1]` fails, as in ANTs. The comparison is made on Linux x86-64; the other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md).
