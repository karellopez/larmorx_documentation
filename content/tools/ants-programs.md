---
title: ImageMath and the ANTs filters
kicker: Tools · ANTs
lede: ImageMath (every operation fMRIPrep, sMRIPrep and sdcflows call), ThresholdImage, MultiplyImages, SmoothImage, ResampleImage and ResampleImageBySpacing, ported from ANTs 2.6.5 and ITK 5.4.5. sMRIPrep's own calls in fMRIPrep's brain extraction are bit-identical; every compared case is identical to ANTs, as built or with correctly rounded maths, but where ANTs reads memory it never wrote.
description: LARMORX's ports of ImageMath, ThresholdImage, MultiplyImages, SmoothImage, ResampleImage and ResampleImageBySpacing, validated against ANTs 2.6.5 and fMRIPrep 25.2.6 — sMRIPrep's brain-extraction calls on their own inputs to inspect, every parity case of each program with its verdict, and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>ports of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span> (each)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/ants-image-math.md') }}">ImageMath</a> · <a href="{{ repo('docs/validation/ants-threshold-image.md') }}">ThresholdImage</a> · <a href="{{ repo('docs/validation/ants-multiply-images.md') }}">MultiplyImages</a> · <a href="{{ repo('docs/validation/ants-smooth-image.md') }}">SmoothImage</a> · <a href="{{ repo('docs/validation/ants-resample-image.md') }}">ResampleImage</a> · <a href="{{ repo('docs/validation/ants-resample-image-by-spacing.md') }}">ResampleImageBySpacing</a></dd>
<dt>Benchmarks</dt><dd><a href="{{ repo('docs/benchmarks/ants-programs.md') }}">programs</a> · <a href="{{ repo('docs/benchmarks/ants-gaussian.md') }}">Gaussian filters and resampling</a> · <a href="{{ repo('docs/benchmarks/ants-morphology.md') }}">morphology</a></dd>
</dl>

## What they are

The small ANTs programs the pipelines call between their larger steps: ImageMath's arithmetic, intensity truncation and rescaling, Gaussian and Laplacian filters, gradients, binary and grayscale morphology, hole filling, padding, connected components and distance maps; Otsu and range thresholds; voxel-wise products; recursive Gaussian and median smoothing; resampling to a size or a spacing.

```bash
larmorx ants ImageMath 3 t1w_trunc.nii.gz TruncateImageIntensity t1w.nii.gz 0.01 0.999 256
larmorx ants ThresholdImage 3 t1w.nii.gz wm.nii.gz Otsu 3 brain_mask.nii.gz
larmorx ants SmoothImage 3 t1w.nii.gz 1 t1w_smooth.nii.gz
larmorx ants ResampleImageBySpacing 3 t1w.nii.gz t1w_2mm.nii.gz 2 2 2
```

In Python: `lx.ants.image_math` and its typed wrappers, `lx.ants.threshold_image`, `lx.ants.otsu_threshold`, `lx.ants.multiply_images`, `lx.ants.smooth_image`, `lx.ants.resample_image`, `lx.ants.resample_image_by_spacing` ([API pages](repo:docs/api/)). How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

One record per program; select a segment to list its cases in that program's explorer below.

{{ ev.agreement('ants-programs', 'image-math') }}

{{ ev.agreement('ants-programs', 'threshold-image') }}

{{ ev.agreement('ants-programs', 'multiply-images') }}

{{ ev.agreement('ants-programs', 'smooth-image') }}

{{ ev.agreement('ants-programs', 'resample-image') }}

{{ ev.agreement('ants-programs', 'resample-image-by-spacing') }}

ImageMath's five cases that pass within a tolerance were run again to classify them: the three `^` cases differ from ANTs as built where glibc's `powf` is not correctly rounded and are bit-identical with CORE-MATH preloaded; in the two signed-zero cases only the sign of a zero differs (ITK keeps the sign of whichever zero its histogram met first; LARMORX defines it), an expected divergence. Where ANTs computes from memory it never wrote, the values are not compared (expected divergences). The cases whose names end in `-known` check a correction against a result known independently (below, "Deliberate corrections"): their verdict is the correction, and their comparison with ANTs runs in reproduce mode, bit for bit, like every other case.

## Worked examples: sMRIPrep's brain extraction {#example}

fMRIPrep 25.2.6 calls ImageMath, ThresholdImage and MultiplyImages in sMRIPrep's brain extraction; the nine calls below are its own, on its own input files from the oracle run of OpenNeuro ds000005 sub-01, by fMRIPrep, by ANTs 2.6.5 at one and eight threads and with correctly rounded maths, and by LARMORX in both modes. Choose the call under *Output*. None of the five oracle runs calls SmoothImage, ResampleImage or ResampleImageBySpacing; their records run generated phantoms and real images.

{{ ev.example('ants-programs', 'brain-extraction-t1w') }}

{{ ev.example('ants-programs', 'brain-extraction-pad') }}

## Deliberate corrections {#deliberate}

Four of ANTs' behaviours were questionable until 2026-10-23, when the project's rules for them decided: where the input makes sense and the result is wrong, LARMORX corrects it by default, warns where the correction changes the output, and keeps ANTs' result one switch away (`upstream_defects="reproduce"`, `LARMORX_UPSTREAM_DEFECTS=reproduce`). Each correction is checked against a result computed another way, bit for bit, in its record:

- **ANTS-17** (`ME`, `MO` with a value): `ME r v` keeps every voxel above 0.5 after eroding the voxels of `v`, so on a label map the other labels survive as 1; LARMORX gives the eroded mask of `v` (SciPy's binary erosion gives the same voxels: `ME-labels-known`, `ME-value-0.3-known`). `MO r 0` erodes nothing (ITK's opening erodes with the background 0) and is a dilation of the zeros; LARMORX opens the zeros (`MO-value-0-known`).
- **ANTS-22** (`PadImage` with a fractional pad): ANTs grows each axis by ⌊2p⌋ voxels and shifts the data by ⌊p⌋, an asymmetric pad (a negative one also misplaces the data by a voxel); LARMORX pads the whole part of p on each side (crops it, for a negative p), the data where the new origin says (NumPy's `pad` and slicing: `pad-fraction-known`, `depad-fraction-known`).
- **ANTS-23** (`ExtractContours` of non-integer values): ITK labels the runs by the truncated value, so 1.2 and 1.7 are one region and 0.6 is background; LARMORX takes every value as its own label (`float-labels-known`, `float-labels-faces-known`).
- **ANTS-32** (ResampleImageBySpacing): the smoothing sigma `out/in − 1` is a number of input voxels, which ANTs passes to ITK as millimetres (on 2 mm voxels, 2 → 4 mm smooths half a voxel); and the points beyond the input get the value at index (1, 1, 1). LARMORX smooths in voxels and gives those points 0 (`sigma-in-voxels-known`: the 2 mm phantom gives exactly what ANTs gives for the same voxels at 1 mm, where its millimetres are voxels; `outside-zero-known`).

The example below is ANTS-17 on a real label map: eroding the white-matter label of fMRIPrep's segmentation of ds000005 sub-01, which ANTs returns with the grey matter and the CSF still in it.

{{ ev.example('ants-programs', 'ants-17') }}

## Every case {#cases}

Each program's record, with what each case tests, its command line, its verdict and the reason. Search, filter by category or verdict, sort by a column; `#case=<program>/<name>` links to one.

### ImageMath {#list-ImageMath}

{{ ev.cases('ants-programs', 'image-math') }}

### ThresholdImage {#list-ThresholdImage}

{{ ev.cases('ants-programs', 'threshold-image') }}

### MultiplyImages {#list-MultiplyImages}

{{ ev.cases('ants-programs', 'multiply-images') }}

### SmoothImage {#list-SmoothImage}

{{ ev.cases('ants-programs', 'smooth-image') }}

### ResampleImage {#list-ResampleImage}

{{ ev.cases('ants-programs', 'resample-image') }}

### ResampleImageBySpacing {#list-ResampleImageBySpacing}

{{ ev.cases('ants-programs', 'resample-image-by-spacing') }}

## Speed {#speed}

{{ ev.speed('ants-programs') }}

## Corrections by default {#corrections}

The records' fix passes meet ANTS-05, ANTS-06, ANTS-08, ANTS-09, ANTS-10, ANTS-12, ANTS-14, ANTS-15, ANTS-16, ANTS-17, ANTS-19, ANTS-20, ANTS-22, ANTS-23 (ImageMath), ANTS-24 (ThresholdImage), ANTS-27 (MultiplyImages), ANTS-28, ANTS-29, ANTS-30, ANTS-31, ANTS-32 (the resamplers) and ITK-02, each corrected by default with `upstream_defects="reproduce"` giving ANTs' behaviour ([register](repo:docs/findings/upstream-defects.md)). None applies to sMRIPrep's calls above. ANTS-30, ResampleImage's corrected command line, awaits the user's review.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, a night at a time: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest night:

{{ ev.random_testing('/tools/ants-programs/') }}

## Known limits {#limits}

ThresholdImage's `Kmeans` is not ported (fMRIPrep does not use it). ResampleImage interpolates with B-splines, Gaussians and windowed sinc in 3D only.
