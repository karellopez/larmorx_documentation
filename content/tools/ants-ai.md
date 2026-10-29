---
title: antsAI and antsAffineInitializer
kicker: Tools · ANTs
lede: >-
  The initial alignments of a registration, ported from ANTs 2.6.5 and ITK 5.4.5: antsAI's
  principal axes, multi-start search and blob alignment, and antsAffineInitializer. Every
  compared case is identical to ANTs, as built or with correctly rounded maths; on fMRIPrep's
  own brain extraction, LARMORX finds ANTs' one-thread transform.
description: LARMORX's ports of antsAI and antsAffineInitializer, validated against ANTs 2.6.5 and fMRIPrep 25.2.6 — the initial transform of sMRIPrep's brain extraction to inspect, as parameters, placed images and distances in mm; antsAI's blob alignment on a real T1w, its blobs, pairs and transforms, with the corrections LARMORX makes; and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>ports of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span> (each)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/ants-ai.md') }}">ants-ai</a> (<a href="{{ repo('docs/validation/ants-ai-full.md') }}">full</a>) · <a href="{{ repo('docs/validation/ants-affine-initializer.md') }}">ants-affine-initializer</a> (<a href="{{ repo('docs/validation/ants-affine-initializer-full.md') }}">full</a>) · benchmark <a href="{{ repo('docs/benchmarks/ants-ai.md') }}">ants-ai</a> · API <a href="{{ repo('docs/api/ants-ai.md') }}">ants-ai</a>, <a href="{{ repo('docs/api/ants-affine-initializer.md') }}">ants-affine-initializer</a></dd>
<dt>Data panel</dt><dd><a href="{{ repo('docs/validation/ants-ai-panel.md') }}">antsAI</a> · <a href="{{ repo('docs/validation/ants-affine-initializer-panel.md') }}">antsAffineInitializer</a></dd>
</dl>

## What they are

Both find a starting transform for a registration: antsAI aligns centres, principal axes or moments, or matched blobs (`-b`), and searches rotations and translations from many starting points against a metric (Mattes, GC, MI); antsAffineInitializer searches rotations about the principal axes. fMRIPrep's `init_aff` steps run antsAI before the brain extraction and the BOLD-to-T1w registration, without blobs.

```bash
larmorx ants antsAI -d 3 -m Mattes[template.nii.gz,t1w.nii.gz,32,Regular,0.25] -x template_mask.nii.gz \
  -t Affine[0.1] -s [15,0.1] -g [40.0,0x40x40] -p 0 -c [10,1e-06,10] -o initialization.mat
larmorx ants antsAffineInitializer 3 fixed.nii.gz moving.nii.gz init.mat 15 0.1 0 10
```

In Python: `lx.ants.ai` (`blobs=30` for `-b 30`), `lx.ants.blob_alignment` (the blob alignment's every step) and `lx.ants.affine_initializer`. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-ai', 'ai') }}

{{ ev.agreement('ants-ai', 'init') }}

Every compared case gives ANTs' exit status, standard output, standard error and transform file, byte for byte, against the unmodified binary at one thread or, where glibc's maths is not correctly rounded, against the same binary with CORE-MATH preloaded. Where ANTs never finishes or seeds its sampling from the clock, LARMORX refuses or is repeatable (expected divergences).

## A worked example: the brain extraction's initial transform {#example}

fMRIPrep's `init_aff`, with its arguments, inputs and seed, and niworkflows' antsAffineInitializer call on the same two images. A transform is shown three ways: the T1w it places on the template (select *Checkerboard* under *Compare* to overlay the template and a placed T1w), its parameters, and how far two transforms send the template's brain apart, in mm.

{{ ev.example('ants-ai', 'init-aff') }}

## Blob alignment {#blobs}

With `-b n`, antsAI starts its search from a transform fitted to matched blobs instead of the centres of mass: up to `n` blobs per image from ANTs' multi-scale Laplacian-of-Gaussian detector; every fixed and moving blob compared by the correlation of their patches (a sphere of radius 20 voxels, turned onto the gradients' principal axes); the best-correlated pairs whose radii agree; the pairs whose distances to at least three others are preserved become landmarks, and a rigid (or affine) transform is fitted to them. LARMORX ports every step, and reproduces ANTs' blobs, correlations, pairs, landmarks and transform bit for bit in `reproduce` mode. ANTs' code has defects that its default corrects ([findings](repo:docs/findings/ants-ai.md#blobs)): its landmark test compares the lengths of the pairs' displacements, not the distances between blobs (ANTS-110), so any rotation leaves it no landmark and a transform of NaNs (ANTS-114); once the correlations run out it pairs the first two blobs again and again (ANTS-111); its detector does not always keep the strongest maxima (ANTS-112); ITK's 2D rigid fit takes −90° near a quarter turn (ITK-60); and it compares the patches in whatever orientation the eigenvectors' signs give, possibly reflected (ANTS-116). At more than one thread ANTs' `-b` crashes (ANTS-60); LARMORX gives its one-thread result at any thread count.

First the blobs: in fMRIPrep's T1w of ds000005 both programs find the same 30 blobs, each drawn here as a sphere of its radius around its voxel (ANTs' from its own code, built with prints: `validation/probes/ants-ai-blobs`).

{{ ev.example('ants-ai', 'blobs-found') }}

Two copies of that T1w with a known transform show what the pairing and the landmark test do. The first is the same voxels with the origin moved: every blob has an identical partner, yet ANTs compares many of those identical patches reflected or turned, pairs eleven blobs (one wrongly) and keeps ten landmarks; it finds the translation exactly. LARMORX's default compares each pair of patches in the orientation that matches best: every identical pair correlates at 1, all thirteen blobs whose patches fit are paired with their true partners and kept, and the copy is placed exactly as the truth places it. The tables list every pair, which program kept it, and how far each transform is from the truth.

{{ ev.example('ants-ai', 'blobs-shift') }}

The second is the T1w rotated by 8 degrees (in millimetres) and shifted: no pair keeps the length of its displacement, ANTs keeps no landmark, and its transform (and LARMORX's in `reproduce` mode, the same file) is NaN. LARMORX's default keeps the pairs whose distances are preserved and finds a rotation close to the truth (the metrics below give the angle and the distance from the true transform).

{{ ev.example('ants-ai', 'blobs-rotated') }}

**ANTS-116, a deliberate correction.** The patch comparison turns the moving patch onto the fixed one with a rotation built from the patches' principal axes; ANTs never checks that rotation for a reflection, and the axes' signs are whatever the eigensolver returns, so identical patches can be compared reflected or turned by 180°. Decided on 2026-10-23 (the input makes sense, the result is wrong): LARMORX tries every sign combination of the axes (four in 3D, two in 2D), each with a proper rotation, and keeps the best correlation; ANTs' own rotation is one of the candidates when it is proper, and reproduce mode keeps ANTs' method. Measured on the T1w above and on blob phantoms with a known transform ([investigation](repo:validation/investigations/ants-116-blob-orientation/README.md)):

{{ ev.table('ants-ai', 'ants-116') }}

Between subjects, or to a template, the patch matching rarely pairs the same anatomy: on the five oracle runs' T1w against MNI152NLin2009cAsym (2 mm), neither keeps a landmark with 30 blobs (the [full tier](repo:docs/validation/ants-ai-full.md)'s `real/*/blobs-mni-rigid` cases). The blob alignment is a rough initialiser for images of one subject.

## On the data panel {#data-panel}

The [data panel](/data-panel/) is the fixed set of fourteen OpenNeuro subjects every tool of LARMORX is validated on: 1.5, 3 and 7 T; Siemens, GE and Philips; single-band, multiband and multi-echo BOLD; a 3.5-year-old to an 82-year-old; a tumour, a stroke with its lesion mask, strong motion. Each record of the panel tier replays every call fMRIPrep 25.2.6 made of the program in its fourteen oracle runs, the node's own `command.txt` with its inputs from the run's working directory (calls repeated word for word are compared once), and runs the program on panel images fMRIPrep never gives it. ANTs runs at one thread, as built and with correctly rounded maths, and at 2 and 3 threads for its own variability where it has any; LARMORX in reproduce mode, and in its default mode for the corrections. The panel's cases are in the case explorers below (categories `panel-fmriprep` and `panel-images`).

**antsAI: 40 of 40 identical to ANTs at one thread** (38 as built, 2 with correctly rounded maths): all 36 calls of the fourteen runs (the brain extraction's initial transform in every run, the BOLD reference's in 22) with fMRIPrep's seed, and four images fMRIPrep never gives it. **antsAffineInitializer: 14 of 14 identical to ANTs as built**, niworkflows' call inside every run's template registration, on its inputs remade exactly. Against fMRIPrep's own transforms (ANTs 2.6.2 at 6 or 8 threads), 31 of the 36 antsAI calls are within 1e-8 in a parameter; five are further, up to 6.8 mm over a 100 mm cube. They are ANTs' own spread above one thread: fMRIPrep's ANTs at one thread gives exactly LARMORX's transform, and at fMRIPrep's thread count both ANTs builds land, run to run, on fMRIPrep's file, on the one-thread result or elsewhere.

{{ ev.table('ants-ai', 'panel-nodes') }}

Images on a small grid (a BOLD reference, a template at 2 mm) are shown as whole volumes; the panel's large anatomical images (up to 17.5 million voxels) as three full-resolution slices through the voxel where LARMORX and ANTs as built differ most (the centre of the field of view where they agree), the whole field of view shown, defaced heads included (the data panel's defacing check).

{{ ev.example('ants-ai', 'panel-init-aff-tumour') }}

{{ ev.table('ants-ai', 'panel-init-aff-tumour-transforms') }}

{{ ev.example('ants-ai', 'panel-init-stroke') }}

{{ ev.table('ants-ai', 'panel-init-stroke-transforms') }}

## Every case {#cases}

Each case of the two records, with what it tests, its verdict and the reason. Search, filter by category or verdict, sort by a column; `#case=<program>/<name>` links to one.

### antsAI {#list-antsAI}

{{ ev.cases('ants-ai', 'ai') }}

### antsAffineInitializer {#list-antsAffineInitializer}

{{ ev.cases('ants-ai', 'init') }}

## Speed {#speed}

antsAI takes about half of ANTs' time at one thread (17.5 s against 31.2 s on a 128 × 128 × 96 head, 79 s against 156 s on the 7 T MP2RAGE and the MNI template) and a sixth or less at eight threads, with ANTs' memory; antsAffineInitializer takes ANTs' time at one thread when it reproduces ANTs (its D13 check of ITK-21 searches twice), half of it in the default mode, and a quarter to a tenth at eight threads. Every transform is ANTs' byte for byte: <a href="{{ repo('docs/benchmarks/ants-ai.md') }}">the benchmark</a> (median of three runs; informal timings on a shared machine).

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/ants-ai/') }}

## Known limits {#limits}

The expected divergences: where ANTs never finishes or crashes (an empty blob list, ANTS-115; `-b` at more than one thread, ANTS-60), LARMORX refuses or gives ANTs' one-thread result; where ANTs seeds its random sampling from the clock (ANTS-58), LARMORX is repeatable. The blob alignment's corrections (ANTS-110, -111, -112, -114, -116 and ITK-60) are LARMORX's default; `upstream_defects="reproduce"` gives ANTs' result bit for bit.
