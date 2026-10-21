---
title: DenoiseImage
kicker: Tools · ANTs
lede: Adaptive non-local means denoising, ported from ANTs 2.6.5 and ITK. ANTs' result changes with its thread count; LARMORX gives ANTs' single-thread result at any thread count.
description: LARMORX's port of ANTs' DenoiseImage, its validation against ANTs 2.6.5 in figures, ANTs' dependence on its thread count, and speed.
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ANTs' and ITK's source (with ITK's AdaptiveDenoising module), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/ants-denoise.md') }}">ants-denoise</a> · benchmark <a href="{{ repo('docs/benchmarks/ants-denoise.md') }}">ants-denoise</a> · API <a href="{{ repo('docs/api/ants-denoise.md') }}">ants-denoise</a> · <a href="{{ repo('docs/findings/ants-denoise.md') }}">findings</a></dd>
</dl>

## What it is

DenoiseImage replaces each voxel by a weighted mean of voxels whose neighbourhoods look alike (patch radius 1 and search radius 2 by default), with a Rician or Gaussian noise model. sMRIPrep calls it on every T1w image before the template is built.

## How to call it

```bash
larmorx ants DenoiseImage -i sub-01_T1w.nii.gz -n Rician -s 1 -o sub-01_desc-denoised_T1w.nii.gz
```

```python
import larmorx as lx

res = lx.ants.denoise_image("sub-01_T1w.nii.gz", n_threads=8)   # sMRIPrep's call
res.denoised.to_filename("sub-01_desc-denoised_T1w.nii.gz")
```

## ANTs' result depends on its thread count

ITK splits the image into slabs, four per thread, and lets them write shared voxels near the slab borders in whatever order the threads run. On ds000005's T1w with sMRIPrep's command line, the [findings](repo:docs/findings/ants-denoise.md) measure 21 % of the voxels changing at 2 threads, 49 % at 4, 82 % at 8 and 85 % at 12, by up to 271; at 8 and 12 threads two runs of ANTs differ from each other. fMRIPrep runs it with its `omp_nthreads` (8 in the oracle run), so its denoised T1w carries one of these multi-thread results. LARMORX computes the single-thread result, whatever `n_threads` is.

{{ figure('ants-denoise/threads', "The share of OpenNeuro ds000005 sub-01's T1w voxels (PDDL-1.0) whose denoised value differs from ANTs' one-thread result, with sMRIPrep's command line (`-n Rician -s 1`): ANTs at 2, 4, 8 and 12 threads, and LARMORX at 1 and 12 threads. LARMORX's remaining difference from ANTs as built comes from glibc's `expf`; with CORE-MATH preloaded into ANTs it is zero.") }}

{{ figure('ants-denoise/thread-maps', "Where the results differ, on a coronal slice inside fMRIPrep's brain mask: the magnitude of the difference from ANTs at one thread on a log scale, voxels that agree left blank. At 2 threads the differences sit in bands around ITK's slab borders; at 12 threads they cover most of the brain. LARMORX at 12 threads differs from ANTs as built in 0.07 % of the brain's voxels, by at most 6 × 10⁻⁵, and is bit-identical to ANTs with correctly rounded maths.") }}

## Agreement with ANTs

The [record](repo:docs/validation/ants-denoise.md) runs 51 cases: 42 pass and 9 are rejected by both programs. Against the unmodified ANTs binary at one thread, 7 of the 40 compared cases are bit-identical; the others differ where glibc's `expf` (or `exp`) is not correctly rounded. With CORE-MATH's functions preloaded into the same binary, 40 of 40 are bit-identical.

{{ figure('ants-denoise/agreement', "The record's 51 cases by category: identical to ANTs as built, identical once ANTs uses correctly rounded maths, `--help`, and the inputs both programs refuse.") }}

Every remaining difference is far inside ANTs' own variability: at most 1.7 × 10⁻⁴ of ANTs' difference between one thread and 2, 4 or 12 threads (the record's table), and in most cases below 10⁻⁶ of it.

{{ figure('ants-denoise/band', "Each differing case's largest difference and one minus its correlation with ANTs as built, divided by ANTs' own difference between one thread and 2, 4 and 12 threads, on a log scale. The case with a patch radius of 0, where ANTs' threads change nothing (a band of 0), is not drawn.") }}

## Speed

{{ figure('ants-denoise/speed', "Median seconds of the whole command for ANTs 2.6.5 and LARMORX at 1 and 12 threads, from the benchmark report of 2026-10-11 (Intel i7-8750H, 12 logical CPUs); the factor is LARMORX's speed-up at one thread. ANTs' multi-thread times are those of its thread-dependent result.") }}

## Corrections by default

The record's fix pass meets ANTS-06, ANTS-43, ANTS-47, ITK-01 and ITK-02, each corrected by default with `upstream_defects="reproduce"` giving ANTs' behaviour ([register](repo:docs/findings/upstream-defects.md)). Nondeterministic behaviour, such as this thread dependence, is never reproduced.

## Known limits

The comparison with ANTs is made on Linux x86-64, against ANTs at one thread; ANTs at several threads has no single result to compare with.
