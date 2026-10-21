---
title: ImageMath and the ANTs filters
kicker: Tools · ANTs
lede: ImageMath (every operation fMRIPrep, sMRIPrep and sdcflows call), ThresholdImage, MultiplyImages, SmoothImage, ResampleImage and ResampleImageBySpacing, ported from ANTs 2.6.5 and ITK 5.4.5.
description: An overview of LARMORX's ports of ImageMath, ThresholdImage, MultiplyImages, SmoothImage, ResampleImage and ResampleImageBySpacing, their validation against ANTs 2.6.5 in figures, and speed.
---

<dl class="facts">
<dt>Implementation</dt><dd>ports of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span> (each)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/ants-image-math.md') }}">ImageMath</a> · <a href="{{ repo('docs/validation/ants-threshold-image.md') }}">ThresholdImage</a> · <a href="{{ repo('docs/validation/ants-multiply-images.md') }}">MultiplyImages</a> · <a href="{{ repo('docs/validation/ants-smooth-image.md') }}">SmoothImage</a> · <a href="{{ repo('docs/validation/ants-resample-image.md') }}">ResampleImage</a> · <a href="{{ repo('docs/validation/ants-resample-image-by-spacing.md') }}">ResampleImageBySpacing</a></dd>
<dt>Benchmarks</dt><dd><a href="{{ repo('docs/benchmarks/ants-programs.md') }}">programs</a> · <a href="{{ repo('docs/benchmarks/ants-gaussian.md') }}">Gaussian filters and resampling</a> · <a href="{{ repo('docs/benchmarks/ants-morphology.md') }}">morphology</a></dd>
</dl>

## What they are

The small ANTs programs the pipelines call between their larger steps: ImageMath's arithmetic, intensity truncation and rescaling, Gaussian and Laplacian filters, gradients, binary and grayscale morphology, hole filling, padding, connected components and distance maps; Otsu and range thresholds; voxel-wise products; recursive Gaussian and median smoothing; resampling to a size or a spacing.

## How to call them

```bash
larmorx ants ImageMath 3 t1w_trunc.nii.gz TruncateImageIntensity t1w.nii.gz 0.01 0.999 256
larmorx ants ThresholdImage 3 t1w.nii.gz wm.nii.gz Otsu 3 brain_mask.nii.gz
larmorx ants SmoothImage 3 t1w.nii.gz 1 t1w_smooth.nii.gz
larmorx ants ResampleImageBySpacing 3 t1w.nii.gz t1w_2mm.nii.gz 2 2 2
```

In Python: `lx.ants.image_math` and its typed wrappers, `lx.ants.threshold_image`, `lx.ants.otsu_threshold`, `lx.ants.multiply_images`, `lx.ants.smooth_image`, `lx.ants.resample_image`, `lx.ants.resample_image_by_spacing` ([API pages](repo:docs/api/)).

## Agreement with ANTs

Over the six records, 513 cases: 448 bit-identical to ANTs 2.6.5 (values and header bytes), 5 ImageMath cases within their declared tolerance (`^` with non-integer powers and signed zeros in grayscale morphology, each with its cause in the record), 6 that pass without values to compare (where ANTs' output depends on memory it never wrote, and usage texts), 2 expected divergences, and 52 inputs both programs refuse.

{{ figure('ants-programs/overview', "The six records' cases, one bar per program: bit-identical to ANTs, within the declared tolerance, passing without values to compare, expected divergences (ThresholdImage's Kmeans, not ported; ResampleImage's B-spline, Gaussian and sinc interpolation of 2D and 4D images) and rejected by both.") }}

{{ figure('ants-programs/image-math', "ImageMath's 327 cases by category of operation.") }}

## Speed

{{ figure('ants-programs/speed', "Median seconds of the whole command for ANTs 2.6.5 and LARMORX at 1 and 12 threads, for a selection of the three benchmark reports' inputs (the pipelines' own calls first; 2026-10-10 and 2026-10-11, Intel i7-8750H, 12 logical CPUs); the factor is LARMORX's speed-up at one thread.") }}

## Corrections by default

The records' fix passes meet ANTS-05, ANTS-06, ANTS-08, ANTS-09, ANTS-10, ANTS-12, ANTS-14, ANTS-15, ANTS-16, ANTS-19, ANTS-20 (ImageMath), ANTS-24 (ThresholdImage), ANTS-27 (MultiplyImages), ANTS-28, ANTS-29, ANTS-30, ANTS-31 (the resamplers) and ITK-02, each corrected by default with `upstream_defects="reproduce"` giving ANTs' behaviour ([register](repo:docs/findings/upstream-defects.md)). ANTS-30, ResampleImage's corrected command line, awaits the user's review.

## Known limits

ThresholdImage's `Kmeans` is not ported (fMRIPrep does not use it). ResampleImage interpolates with B-splines, Gaussians and windowed sinc in 3D only.
