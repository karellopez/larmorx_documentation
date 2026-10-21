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

ImageMath's five cases that pass within a tolerance were run again to classify them: the three `^` cases differ from ANTs as built where glibc's `powf` is not correctly rounded and are bit-identical with CORE-MATH preloaded; in the two signed-zero cases only the sign of a zero differs (ITK keeps the sign of whichever zero its histogram met first; LARMORX defines it), an expected divergence. Where ANTs computes from memory it never wrote, the values are not compared (expected divergences).

## Worked examples: sMRIPrep's brain extraction {#example}

fMRIPrep 25.2.6 calls ImageMath, ThresholdImage and MultiplyImages in sMRIPrep's brain extraction; the nine calls below are its own, on its own input files from the oracle run of OpenNeuro ds000005 sub-01, by fMRIPrep, by ANTs 2.6.5 at one and eight threads and with correctly rounded maths, and by LARMORX in both modes. Choose the call under *Output*. None of the five oracle runs calls SmoothImage, ResampleImage or ResampleImageBySpacing; their records run generated phantoms and real images.

{{ ev.example('ants-programs', 'brain-extraction-t1w') }}

{{ ev.example('ants-programs', 'brain-extraction-pad') }}

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

The records' fix passes meet ANTS-05, ANTS-06, ANTS-08, ANTS-09, ANTS-10, ANTS-12, ANTS-14, ANTS-15, ANTS-16, ANTS-19, ANTS-20 (ImageMath), ANTS-24 (ThresholdImage), ANTS-27 (MultiplyImages), ANTS-28, ANTS-29, ANTS-30, ANTS-31 (the resamplers) and ITK-02, each corrected by default with `upstream_defects="reproduce"` giving ANTs' behaviour ([register](repo:docs/findings/upstream-defects.md)). None applies to sMRIPrep's calls above. ANTS-30, ResampleImage's corrected command line, awaits the user's review.

## Known limits {#limits}

ThresholdImage's `Kmeans` is not ported (fMRIPrep does not use it). ResampleImage interpolates with B-splines, Gaussians and windowed sinc in 3D only.
