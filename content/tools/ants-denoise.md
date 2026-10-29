---
title: DenoiseImage
kicker: Tools · ANTs
lede: Adaptive non-local means denoising, ported from ANTs 2.6.5 and ITK. ANTs' result changes with its thread count (in 85 % of a T1w's voxels at 12 threads); LARMORX gives ANTs' single-thread result at any thread count, and corrects ANTS-43 and ANTS-44 by default.
description: LARMORX's port of ANTs' DenoiseImage, validated against ANTs 2.6.5 and fMRIPrep 25.2.6 — fMRIPrep's denoising of a real T1w to inspect, ANTs at 1 to 12 threads and repeated, ANTS-43 and ANTS-44 corrected, every parity case with its verdict, and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ANTs' and ITK's source (with ITK's AdaptiveDenoising module), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/ants-denoise.md') }}">ants-denoise</a> · benchmark <a href="{{ repo('docs/benchmarks/ants-denoise.md') }}">ants-denoise</a> · API <a href="{{ repo('docs/api/ants-denoise.md') }}">ants-denoise</a> · findings <a href="{{ repo('docs/findings/ants-denoise.md') }}">ants-denoise</a></dd>
<dt>Data panel</dt><dd><a href="{{ repo('docs/validation/ants-denoise-panel.md') }}">ants-denoise-panel</a></dd>
</dl>

## What it is

DenoiseImage replaces each voxel by a weighted mean of voxels whose neighbourhoods look alike (patch radius 1 and search radius 2 by default), with a Rician or Gaussian noise model. sMRIPrep calls it on every T1w image before the template is built.

```bash
larmorx ants DenoiseImage -i sub-01_T1w.nii.gz -n Rician -s 1 -o sub-01_desc-denoised_T1w.nii.gz
```

```python
import larmorx as lx

res = lx.ants.denoise_image("sub-01_T1w.nii.gz", n_threads=8)   # sMRIPrep's call
res.denoised.to_filename("sub-01_desc-denoised_T1w.nii.gz")
```

How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-denoise', 'port') }}

Every case that produces an image is bit-identical to ANTs at one thread: as built where glibc's `expf` is correctly rounded for every value the run meets, otherwise once the same binary uses CORE-MATH's correctly rounded functions. The invalid inputs are refused by both programs.

## A worked example: fMRIPrep's own denoising {#example}

The first step of fMRIPrep's anatomical workflow, with its own arguments, by ANTs at 1, 2, 3, 4, 8 and 12 threads (six times at 8 and three at 12), by fMRIPrep's own ANTs, and by LARMORX. ITK's threads share the image in slabs, four per thread, and write the voxels near each slab's border in turn: on the coronal slice below, ANTs at 8 threads departs from its one-thread result in bands along the slabs. fMRIPrep's own run, at 8 threads with its ANTs 2.6.2 build, differs from ANTs 2.6.5 at 8 threads, although the two builds agree bit for bit at one thread. LARMORX's default mode then corrects ANTS-43, where ITK's Rician correction factor becomes NaN.

{{ ev.example('ants-denoise', 'fmriprep-denoise') }}

## A deliberate correction: the bias outside a mask (ANTS-44) {#ants-44}

With a mask (`-x`) and the Rician noise model, the patches of the centres in the mask reach the voxels just outside it, which are denoised like the others. ITK smooths and corrects the Rician bias only inside the mask: outside it, those voxels keep the raw noise estimate of the last centre that reached them, an unsmoothed value on the mask's edge. Decided on 2026-10-23 (the input makes sense, the result is wrong): LARMORX gives them the smoothed and corrected bias, as inside; the voxels no centre reached are not denoised, as in ITK; reproduce mode gives ANTs' output. fMRIPrep denoises without a mask, so its own call is unchanged; the example is a user's call, fMRIPrep's preprocessed T1w of ds000005 denoised within its brain mask.

{{ ev.example('ants-denoise', 'ants-44') }}

## Against ANTs' own variability {#variability}

Where LARMORX differs from ANTs as built (glibc's `expf`), the record sets the difference against ANTs' own difference between one thread and 2, 4 and 12 threads.

{{ ev.band('ants-denoise') }}

## On the data panel {#data-panel}

The [data panel](/data-panel/) is the fixed set of fourteen OpenNeuro subjects every tool of LARMORX is validated on: 1.5, 3 and 7 T; Siemens, GE and Philips; single-band, multiband and multi-echo BOLD; a 3.5-year-old to an 82-year-old; a tumour, a stroke with its lesion mask, strong motion. Each record of the panel tier replays every call fMRIPrep 25.2.6 made of the program in its fourteen oracle runs, the node's own `command.txt` with its inputs from the run's working directory (calls repeated word for word are compared once), and runs the program on panel images fMRIPrep never gives it. ANTs runs at one thread, as built and with correctly rounded maths, and at 2 and 3 threads for its own variability where it has any; LARMORX in reproduce mode, and in its default mode for the corrections. The panel's cases are in the case explorers below (categories `panel-fmriprep` and `panel-images`).

**21 of 21 bit-identical to ANTs with correctly rounded maths**: sMRIPrep's denoising of every T1w of the fourteen runs (17 calls, the 3.5-year-old, the glioma, the stroke, strong motion, 1.5 T and 7 T among them) and four images fMRIPrep never denoises (the 7 T MP2RAGE, the 82-year-old's FLAIR, a child's T2w, the 1.5 T T1w with the Gaussian model). Against ANTs as built, glibc's `expf` moves voxels in every case, by at most 0.0015 of ANTs' own difference between one thread and two or three.

{{ ev.table('ants-denoise', 'panel-nodes') }}

Images on a small grid (a BOLD reference, a template at 2 mm) are shown as whole volumes; the panel's large anatomical images (up to 17.5 million voxels) as three full-resolution slices through the voxel where LARMORX and ANTs as built differ most (the centre of the field of view where they agree), the whole field of view shown, defaced heads included (the data panel's defacing check).

{{ ev.example('ants-denoise', 'panel-7t') }}

{{ ev.example('ants-denoise', 'panel-motion') }}

{{ ev.example('ants-denoise', 'panel-flair') }}

{{ ev.example('ants-denoise', 'panel-child-t2w') }}

## Every case {#cases}

Each case of the record, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('ants-denoise') }}

## Speed {#speed}

{{ ev.speed('ants-denoise') }}

## Corrections by default {#corrections}

The record's fix pass meets ANTS-06, ANTS-43, ANTS-44, ANTS-47, ITK-01 and ITK-02, each corrected by default with `upstream_defects="reproduce"` (or `LARMORX_UPSTREAM_DEFECTS=reproduce`) giving ANTs' behaviour ([register](repo:docs/findings/upstream-defects.md)). ANTS-43 changes sMRIPrep's own command, as the worked example measures. Nondeterministic behaviour, such as the thread dependence (ANTS-42), is never reproduced.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/ants-denoise/') }}

## Known limits {#limits}

The comparison with ANTs is made on Linux x86-64, against ANTs at one thread; ANTs at several threads has no single result to compare with. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md).
