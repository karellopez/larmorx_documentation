---
title: DenoiseImage
kicker: Evidence · ANTs
lede: >-
  `DenoiseImage` replaces each voxel by a weighted mean of the voxels whose neighbourhoods look
  alike, with a Rician or Gaussian noise model. LARMORX's port is a replica of ANTs 2.6.5's
  program on ITK 5.4.5. In `reproduce` it gives ANTs' one-thread output bit for bit in every
  compared case of its two records once ANTs uses correctly rounded maths (40 of 40 and 21 of
  21). With ANTs as built, 7 of the 40 and none of the 21 match bit for bit; the others differ
  only where glibc's `expf` is not correctly rounded.
  ANTs' own result changes with its thread count, in 85 % of a T1w's voxels at 12 threads; the
  replica gives ANTs' one-thread result on any number of threads. Its default, `fix`, corrects
  ANTS-43 and ANTS-44.
description: >-
  How LARMORX's replica of ANTs' DenoiseImage compares with ANTs 2.6.5 and fMRIPrep 25.2.6:
  fMRIPrep's denoising of a real T1w by ANTs at 1 to 12 threads and repeated, the corrections
  ANTS-43 and ANTS-44, four images of the data panel, ANTs' own variability between thread
  counts, every case of the two records with its verdict, random testing and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: translated from ANTs 2.6.5's and ITK 5.4.5's source, with ITK's AdaptiveDenoising module (Apache-2.0)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span>, with its data panel (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/ants-denoise.md') }}">standard comparison</a> (ANTs 2.6.5), <a href="{{ repo('docs/validation/ants-denoise-panel.md') }}">data panel</a> (ANTs 2.6.5) · benchmark <a href="{{ repo('docs/benchmarks/ants-denoise.md') }}">ants-denoise</a> · findings <a href="{{ repo('docs/findings/ants-denoise.md') }}">ants-denoise</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/ants-denoise.md') }}">ants-denoise</a></dd>
</dl>

## What is compared {#what-it-is}

`DenoiseImage` replaces each voxel by a weighted mean of voxels whose neighbourhoods look alike (patch radius 1 and search radius 2 by default), with a Rician or Gaussian noise model. sMRIPrep calls it on every T1w image before the template is built.

The replica runs beside ANTs 2.6.5's `DenoiseImage` on the same files with the same arguments. ANTs is the repository's build (GCC 14.3, with ITK's AdaptiveDenoising module), run on one thread as built and with correctly rounded maths, and at more threads for its own variability. fMRIPrep's own ANTs 2.6.2 runs too, in fMRIPrep's image.

```bash
larmorx ants DenoiseImage -i sub-01_T1w.nii.gz -n Rician -s 1 -o sub-01_desc-denoised_T1w.nii.gz
```

```python
import larmorx as lx

# sMRIPrep's call
res = lx.ants.denoise_image("sub-01_T1w.nii.gz", n_threads=8)
res.denoised.to_filename("sub-01_desc-denoised_T1w.nii.gz")
```

The [API page](repo:docs/api/ants-denoise.md) maps every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its port {#ports}

ANTs and ITK come under the Apache-2.0 licence, as LARMORX does, so the replica is in `larmorx` itself. It is translated from ANTs' and ITK's source, step by step, to give their results bit for bit. A clean room of ANTs' programs is planned after FreeSurfer ([roadmap](/roadmap/)).

ANTs' `DenoiseImage` changes with its thread count (ANTS-42); the replica gives ANTs' single-thread result on any number of threads. It computes `expf` correctly rounded, the same on every platform, which is why ANTs as built differs from it in the last bits where glibc's is not.

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-denoise', 'port') }}

In `reproduce`, every case that produces an image gives ANTs' output at one thread bit for bit: as ANTs is built where glibc's `expf` is correctly rounded for every value the run meets, otherwise once the same ANTs binary uses CORE-MATH's correctly rounded functions. The invalid inputs are refused by both programs. Nothing is open.

## In fMRIPrep: denoising a real T1w {#example}

The first step of fMRIPrep's anatomical workflow, with its own arguments, by ANTs at 1, 2, 3, 4, 8 and 12 threads (six times at 8 and three at 12), by fMRIPrep's own ANTs, and by the replica. ITK's threads share the image in slabs, four per thread, and write the voxels near each slab's border in turn: on the coronal slice below, ANTs at 8 threads departs from its one-thread result in bands along the slabs. fMRIPrep's own run, at 8 threads with its ANTs 2.6.2 build, differs from ANTs 2.6.5 at 8 threads, although the two builds agree bit for bit at one thread. The replica's default, `fix`, then corrects ANTS-43, where ITK's Rician correction factor becomes NaN (the row *replica, fix − reproduce*). Choose the panels, the plane, the slice and the window; select a point to read every panel's exact value there; set two images side by side, swipe or blink between them.

{{ ev.example('ants-denoise', 'fmriprep-denoise') }}

## A deliberate correction: the bias outside a mask (ANTS-44) {#ants-44}

With a mask (`-x`) and the Rician noise model, the patches of the centres in the mask reach the voxels just outside it, which are denoised like the others. ITK smooths and corrects the Rician bias only inside the mask: outside it, those voxels keep the raw noise estimate of the last centre that reached them, an unsmoothed value on the mask's edge. The input makes sense and the result is wrong, so the replica's default, `fix`, gives them the smoothed and corrected bias, as inside; the voxels no centre reached are not denoised, as in ITK; `reproduce` gives ANTs' output. fMRIPrep denoises without a mask, so its own call is unchanged; the example is a user's call, fMRIPrep's preprocessed T1w of ds000005 denoised within its brain mask.

{{ ev.example('ants-denoise', 'ants-44') }}

## Against the original's own variability {#variability}

Where the replica differs from ANTs as built (glibc's `expf`), the record sets the difference against ANTs' own difference between one thread and 2, 4 and 12 threads.

{{ ev.band('ants-denoise') }}

## On the data panel {#data-panel}

The [data panel](/data-panel/) is the fixed set of fourteen OpenNeuro subjects on which LARMORX's programs are validated: 1.5, 3 and 7 T; Siemens, GE and Philips; single-band, multiband and multi-echo BOLD; a 3.5-year-old to an 82-year-old; a tumour, a stroke with its lesion mask, strong motion. Its record replays every call fMRIPrep 25.2.6 made of the program in its fourteen runs on these subjects, the node's own `command.txt` with its inputs from the run's working directory (calls repeated word for word are compared once), and runs the program on panel images fMRIPrep never gives it. ANTs runs at one thread, as built and with correctly rounded maths, and at 2 and 3 threads for its own variability where it has any; the replica in `reproduce`, and in `fix` for the corrections. The panel's cases are in the case explorer below (the categories *data panel: fMRIPrep's calls* and *data panel: other images*).

**21 of 21 bit-identical to ANTs with correctly rounded maths**: sMRIPrep's denoising of every T1w of the fourteen runs (17 calls, the 3.5-year-old, the glioma, the stroke, strong motion, 1.5 T and 7 T among them) and four images fMRIPrep never denoises (the 7 T MP2RAGE, the 82-year-old's FLAIR, a child's T2w, the 1.5 T T1w with the Gaussian model). Against ANTs as built, glibc's `expf` moves voxels in every case, by at most 0.0015 of ANTs' own difference between one thread and two or three.

{{ ev.table('ants-denoise', 'panel-nodes') }}

Images on a small grid (a BOLD reference, a template at 2 mm) are shown as whole volumes; the panel's large anatomical images (up to 17.5 million voxels) as three full-resolution slices through the voxel where the replica and ANTs as built differ most (the centre of the field of view where they agree), the whole field of view shown, defaced heads included (the data panel's defacing check).

{{ ev.example('ants-denoise', 'panel-7t') }}

{{ ev.example('ants-denoise', 'panel-motion') }}

{{ ev.example('ants-denoise', 'panel-flair') }}

{{ ev.example('ants-denoise', 'panel-child-t2w') }}

## Every case {#cases}

Each case of the two records, the standard comparison and the data panel, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('ants-denoise') }}

## Speed {#speed}

The wall time of the whole command on six real images, from a BOLD reference and a field map's magnitude to sMRIPrep's call on two raw T1w images, with ANTs and the replica at 1 and 12 threads ([benchmark](repo:docs/benchmarks/ants-denoise.md)).

{{ ev.speed('ants-denoise') }}

## Corrections by default {#corrections}

Where ANTs has a deterministic defect that changes a result, the replica corrects it by default, `fix`, and warns. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives ANTs' behaviour, and the records compare with it. The record's list of what `fix` changed meets ANTS-06, ANTS-43, ANTS-44, ANTS-47, ITK-01 and ITK-02 ([register](repo:docs/findings/upstream-defects.md)). ANTS-43 changes sMRIPrep's own command, as the worked example measures. Nondeterministic behaviour, such as the thread dependence (ANTS-42), is never reproduced.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original and the replica, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a case of the record, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/ants-denoise/', 'ants-denoise') }}

## Known limits {#limits}

The comparison with ANTs is made on Linux x86-64, against ANTs at one thread; ANTs at several threads has no single result to compare with. The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output.

## History {#history}

- **2026-10-12**: ANTS-43 corrected by default ([register](repo:docs/findings/upstream-defects.md#summary)).
- **2026-10-21**: the same command run again by ANTs 2.6.5, six times at 8 threads and three times at 12: one result each (earlier runs at 8 threads differed, [findings](repo:docs/findings/ants-denoise.md)).
- **2026-10-23**: ANTS-44 decided and corrected by default.
- **2026-10-26**: the data panel's record, sMRIPrep's denoising of every T1w of the fourteen runs and four more images.
