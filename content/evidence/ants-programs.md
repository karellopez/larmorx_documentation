---
title: ImageMath and the ANTs filters
kicker: Evidence · ANTs
lede: >-
  `ImageMath` and five smaller ANTs programs, `ThresholdImage`, `MultiplyImages`,
  `SmoothImage`, `ResampleImage` and `ResampleImageBySpacing`, do the arithmetic, filters,
  morphology, thresholds and resampling that the pipelines call between their larger steps.
  LARMORX's port of each is a replica of ANTs 2.6.5's program on ITK 5.4.5. In `reproduce`,
  ImageMath's replica gives ANTs' values bit for bit in 306 of the 308 compared cases of its
  standard comparison once ANTs uses correctly rounded maths, and in all 374 of its data panel;
  in the other two only the sign of a zero differs. With ANTs as built, 303 of the 308 match;
  three more differ only where glibc's `powf` is not correctly rounded, and the two signed zeros
  as above. The other five replicas give
  ANTs' values and header bytes bit for bit in every compared case of their records, and
  sMRIPrep's own calls in fMRIPrep's brain extraction give ANTs' and fMRIPrep's bytes. Their
  default, `fix`, corrects 22 defects of ANTs and ITK, none of which changes those calls.
description: >-
  How LARMORX's replicas of ANTs' ImageMath, ThresholdImage, MultiplyImages, SmoothImage,
  ResampleImage and ResampleImageBySpacing compare with ANTs 2.6.5 and fMRIPrep 25.2.6:
  sMRIPrep's brain-extraction calls on their own inputs, ANTS-17 corrected on a real label map,
  five images of the data panel, every case of each program's records with its verdict, and
  speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: each program translated from ANTs 2.6.5's and ITK 5.4.5's source (Apache-2.0)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span>, each program, with its data panel (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd>standard comparison: <a href="{{ repo('docs/validation/ants-image-math.md') }}">ImageMath</a> · <a href="{{ repo('docs/validation/ants-threshold-image.md') }}">ThresholdImage</a> · <a href="{{ repo('docs/validation/ants-multiply-images.md') }}">MultiplyImages</a> · <a href="{{ repo('docs/validation/ants-smooth-image.md') }}">SmoothImage</a> · <a href="{{ repo('docs/validation/ants-resample-image.md') }}">ResampleImage</a> · <a href="{{ repo('docs/validation/ants-resample-image-by-spacing.md') }}">ResampleImageBySpacing</a>; data panel: <a href="{{ repo('docs/validation/ants-image-math-panel.md') }}">ImageMath</a> · <a href="{{ repo('docs/validation/ants-threshold-image-panel.md') }}">ThresholdImage</a> · <a href="{{ repo('docs/validation/ants-multiply-images-panel.md') }}">MultiplyImages</a> · <a href="{{ repo('docs/validation/ants-smooth-image-panel.md') }}">SmoothImage</a> · <a href="{{ repo('docs/validation/ants-resample-image-panel.md') }}">ResampleImage</a> · <a href="{{ repo('docs/validation/ants-resample-image-by-spacing-panel.md') }}">ResampleImageBySpacing</a>; all against ANTs 2.6.5</dd>
<dt>Benchmarks</dt><dd><a href="{{ repo('docs/benchmarks/ants-programs.md') }}">programs</a> · <a href="{{ repo('docs/benchmarks/ants-gaussian.md') }}">Gaussian filters and resampling</a> · <a href="{{ repo('docs/benchmarks/ants-morphology.md') }}">morphology</a></dd>
<dt>Reference</dt><dd><a href="{{ link('/programs/ants/MultiplyImages/') }}"><code>MultiplyImages</code></a> · API pages <a href="{{ repo('docs/api/ants-image-math.md') }}">ants-image-math</a> · <a href="{{ repo('docs/api/ants-threshold-image.md') }}">ants-threshold-image</a> · <a href="{{ repo('docs/api/ants-multiply-images.md') }}">ants-multiply-images</a> · <a href="{{ repo('docs/api/ants-smooth-image.md') }}">ants-smooth-image</a> · <a href="{{ repo('docs/api/ants-resample-image.md') }}">ants-resample-image</a> · <a href="{{ repo('docs/api/ants-resample-image-by-spacing.md') }}">ants-resample-image-by-spacing</a> · findings <a href="{{ repo('docs/findings/ants-image-programs.md') }}">ants-image-programs</a></dd>
</dl>

## What is compared {#what-they-are}

The small ANTs programs the pipelines call between their larger steps: ImageMath's arithmetic, intensity truncation and rescaling, Gaussian and Laplacian filters, gradients, binary and grayscale morphology, hole filling, padding, connected components and distance maps; Otsu and range thresholds; voxel-wise products; recursive Gaussian and median smoothing; resampling to a size or a spacing.

Each replica runs beside ANTs 2.6.5's program on the same files with the same arguments. ANTs is the repository's build (GCC 14.3), run as built and with correctly rounded maths, at one thread in the records and at more for its own variability. In sMRIPrep's brain extraction, fMRIPrep's own ANTs 2.6.2 runs too, in fMRIPrep's image.

```bash
larmorx ants ImageMath 3 t1w_trunc.nii.gz TruncateImageIntensity t1w.nii.gz 0.01 0.999 256
larmorx ants ThresholdImage 3 t1w.nii.gz wm.nii.gz Otsu 3 brain_mask.nii.gz
larmorx ants SmoothImage 3 t1w.nii.gz 1 t1w_smooth.nii.gz
larmorx ants ResampleImageBySpacing 3 t1w.nii.gz t1w_2mm.nii.gz 2 2 2
```

In Python: `lx.ants.image_math` and its typed wrappers, `lx.ants.threshold_image`, `lx.ants.otsu_threshold`, `lx.ants.multiply_images`, `lx.ants.smooth_image`, `lx.ants.resample_image`, `lx.ants.resample_image_by_spacing` ([API pages](repo:docs/api/)). How to read what follows: [how to read the evidence](/validation/#reading).

### Their port {#ports}

ANTs and ITK come under the Apache-2.0 licence, as LARMORX does, so the replicas are in `larmorx` itself. Each is translated from ANTs' and ITK's source, step by step, to give their results bit for bit. A clean room of ANTs' programs is planned after FreeSurfer ([roadmap](/roadmap/)).

The replicas compute the C library's maths correctly rounded, the same on every platform. Where glibc's `powf` is not correctly rounded for a value a run meets, ANTs as built differs from them in the last bits.

## The verdicts at a glance {#verdicts}

One chart per program, over its standard comparison and its data panel; select a segment to list its cases in that program's explorer below.

{{ ev.agreement('ants-programs', 'image-math') }}

{{ ev.agreement('ants-programs', 'threshold-image') }}

{{ ev.agreement('ants-programs', 'multiply-images') }}

{{ ev.agreement('ants-programs', 'smooth-image') }}

{{ ev.agreement('ants-programs', 'resample-image') }}

{{ ev.agreement('ants-programs', 'resample-image-by-spacing') }}

ImageMath's five cases that pass within a tolerance were run again to classify them: the three `^` cases differ from ANTs as built where glibc's `powf` is not correctly rounded and are bit-identical once ANTs uses correctly rounded maths; in the two signed-zero cases only the sign of a zero differs (ITK keeps the sign of whichever zero its histogram met first; the replica defines it), an expected divergence. Where ANTs computes from memory it never wrote, the values are not compared (expected divergences). The cases whose names end in `-known` check a correction against a result known independently (below, "Corrections checked against known results"): their verdict is the correction, and their comparison with ANTs runs in `reproduce`, bit for bit, like every other case.

## In sMRIPrep: the brain extraction, step by step {#example}

fMRIPrep 25.2.6 calls ImageMath, ThresholdImage and MultiplyImages in sMRIPrep's brain extraction. The nine calls below are its own, on its own input files from fMRIPrep's run of OpenNeuro ds000005 sub-01: by fMRIPrep, by ANTs 2.6.5 at one and eight threads and with correctly rounded maths, and by the replica in `fix` and in `reproduce`. Choose the call under *Output*. None of the five fMRIPrep runs calls SmoothImage, ResampleImage or ResampleImageBySpacing; their records run generated phantoms and real images.

{{ ev.example('ants-programs', 'brain-extraction-t1w') }}

{{ ev.example('ants-programs', 'brain-extraction-pad') }}

## Corrections checked against known results {#deliberate}

Where the input makes sense and ANTs' result is wrong, the replica corrects it by default, warns where the correction changes the output, and keeps ANTs' result one switch away: `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1). Each of these four corrections is checked against a result computed another way, bit for bit, in its record:

- **ANTS-17** (`ME`, `MO` with a value): `ME r v` keeps every voxel above 0.5 after eroding the voxels of `v`, so on a label map the other labels survive as 1; the replica gives the eroded mask of `v` (SciPy's binary erosion gives the same voxels: `ME-labels-known`, `ME-value-0.3-known`). `MO r 0` erodes nothing (ITK's opening erodes with the background 0) and is a dilation of the zeros; the replica opens the zeros (`MO-value-0-known`).
- **ANTS-22** (`PadImage` with a fractional pad): ANTs grows each axis by ⌊2p⌋ voxels and shifts the data by ⌊p⌋, an asymmetric pad (a negative one also misplaces the data by a voxel); the replica pads the whole part of p on each side (crops it, for a negative p), the data where the new origin says (NumPy's `pad` and slicing: `pad-fraction-known`, `depad-fraction-known`).
- **ANTS-23** (`ExtractContours` of non-integer values): ITK labels the runs by the truncated value, so 1.2 and 1.7 are one region and 0.6 is background; the replica takes every value as its own label (`float-labels-known`, `float-labels-faces-known`).
- **ANTS-32** (ResampleImageBySpacing): the smoothing sigma `out/in − 1` is a number of input voxels, which ANTs passes to ITK as millimetres (on 2 mm voxels, 2 → 4 mm smooths half a voxel); and the points beyond the input get the value at index (1, 1, 1). The replica smooths in voxels and gives those points 0 (`sigma-in-voxels-known`: the 2 mm phantom gives exactly what ANTs gives for the same voxels at 1 mm, where its millimetres are voxels; `outside-zero-known`).

The example below is ANTS-17 on a real label map: eroding the white-matter label of fMRIPrep's segmentation of ds000005 sub-01, which ANTs returns with the grey matter and the CSF still in it.

{{ ev.example('ants-programs', 'ants-17') }}

## On the data panel {#data-panel}

The [data panel](/validation/data-panel/) is the fixed set of fourteen OpenNeuro subjects on which LARMORX's programs are validated: 1.5, 3 and 7 T; Siemens, GE and Philips; single-band, multiband and multi-echo BOLD; a 3.5-year-old to an 82-year-old; a tumour, a stroke with its lesion mask, strong motion. Each record of the data panel replays every call fMRIPrep 25.2.6 made of the program in its fourteen runs, the node's own `command.txt` with its inputs from the run's working directory (calls repeated word for word are compared once), and runs the program on panel images fMRIPrep never gives it. ANTs runs at one thread, as built and with correctly rounded maths, and at 2 and 3 threads for its own variability where it has any; the replica in `reproduce`, and in `fix` for the corrections. The panel's cases are in the case explorers below (categories *data panel: fMRIPrep's calls* and *data panel: other images*).

**ImageMath: 374 of 374 compared cases bit-identical, headers in 374**: every ImageMath call of the fourteen runs (sMRIPrep's brain extraction and template steps, sdcflows' and fMRIPrep's masks) and the panel's own images (truncation of the 7 T MP2RAGE, the FLAIR and the 1.5 T T1w, Laplacians, the lesion mask's components, a 600-volume series). **ThresholdImage 18 of 18, MultiplyImages 44 of 44, SmoothImage 4 of 4 (a zero sigma along time refused by both), ResampleImage 4 of 4, ResampleImageBySpacing 3 of 3 bit-identical**, header bytes included; fMRIPrep calls the last three on none of its runs, so their cases are the panel's images.

{{ ev.table('ants-programs', 'panel-nodes-image-math') }}

{{ ev.table('ants-programs', 'panel-nodes-threshold-image') }}

{{ ev.table('ants-programs', 'panel-nodes-multiply-images') }}

Images on a small grid (a BOLD reference, a template at 2 mm) are shown as whole volumes; the panel's large anatomical images (up to 17.5 million voxels) as three full-resolution slices through the voxel where the replica and ANTs as built differ most (the centre of the field of view where they agree), the whole field of view shown, defaced heads included (the data panel's defacing check).

{{ ev.example('ants-programs', 'panel-truncate-7t') }}

{{ ev.example('ants-programs', 'panel-smooth-flair') }}

{{ ev.example('ants-programs', 'panel-otsu-7t') }}

{{ ev.example('ants-programs', 'panel-multiply-stroke') }}

{{ ev.example('ants-programs', 'panel-laplacian-toddler') }}

## Every case {#cases}

Each program's records, with what each case tests, its command line, its verdict and the reason. Search, filter by category or verdict, sort by a column; `#case=<program>/<name>` links to one.

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

Each program on the images the pipelines give it, the pipelines' own calls first, from the three benchmark reports above.

{{ ev.speed('ants-programs') }}

## Corrections by default {#corrections}

The records' `fix` passes meet ANTS-05, ANTS-06, ANTS-08, ANTS-09, ANTS-10, ANTS-12, ANTS-14, ANTS-15, ANTS-16, ANTS-17, ANTS-19, ANTS-20, ANTS-22, ANTS-23 (ImageMath), ANTS-24 (ThresholdImage), ANTS-27 (MultiplyImages), ANTS-28, ANTS-29, ANTS-30, ANTS-31, ANTS-32 (the resamplers) and ITK-02. The replicas correct each by default; in `reproduce` they give ANTs' behaviour ([register](repo:docs/findings/upstream-defects.md)). None applies to sMRIPrep's calls above. ANTS-30 is ResampleImage's seventh argument, which ANTs reads twice; the replica's command line for it is designed on its [API page](repo:docs/api/ants-resample-image.md).

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and the replica, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a comparison case, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/evidence/ants-programs/', 'ants-programs') }}

## Known limits {#limits}

ThresholdImage's `Kmeans` is not ported (fMRIPrep does not use it). ResampleImage interpolates with B-splines, Gaussians and windowed sinc in 3D only.

## History {#history}

- **2026-10-12:** ANTS-30, ResampleImage's seventh argument read twice, corrected by default (the register's row).
- **2026-10-22:** the user approved the replica's command line for ANTS-30 (the register's row).
- **2026-10-23:** four of ANTs' behaviours that were questionable (ANTS-17, ANTS-22, ANTS-23 and ANTS-32) were decided by the project's rules for them: corrected by default, each checked against a result known independently.
- **2026-10-26 and 2026-10-27:** the data panel's records of the six programs (ImageMath's on 2026-10-27; their Generated lines).
