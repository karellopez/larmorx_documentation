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
<dt>Records</dt><dd><a href="{{ repo('docs/validation/ants-ai.md') }}">ants-ai</a> (<a href="{{ repo('docs/validation/ants-ai-full.md') }}">full</a>) · <a href="{{ repo('docs/validation/ants-affine-initializer.md') }}">ants-affine-initializer</a> (<a href="{{ repo('docs/validation/ants-affine-initializer-full.md') }}">full</a>) · API <a href="{{ repo('docs/api/ants-ai.md') }}">ants-ai</a>, <a href="{{ repo('docs/api/ants-affine-initializer.md') }}">ants-affine-initializer</a></dd>
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

With `-b n`, antsAI starts its search from a transform fitted to matched blobs instead of the centres of mass: up to `n` blobs per image from ANTs' multi-scale Laplacian-of-Gaussian detector; every fixed and moving blob compared by the correlation of their patches (a sphere of radius 20 voxels, turned onto the gradients' principal axes); the best-correlated pairs whose radii agree; the pairs whose distances to at least three others are preserved become landmarks, and a rigid (or affine) transform is fitted to them. LARMORX ports every step, and reproduces ANTs' blobs, correlations, pairs, landmarks and transform bit for bit in `reproduce` mode. ANTs' code has defects that its default corrects ([findings](repo:docs/findings/ants-ai.md#blobs)): its landmark test compares the lengths of the pairs' displacements, not the distances between blobs (ANTS-110), so any rotation leaves it no landmark and a transform of NaNs (ANTS-114); once the correlations run out it pairs the first two blobs again and again (ANTS-111); its detector does not always keep the strongest maxima (ANTS-112); ITK's 2D rigid fit takes −90° near a quarter turn (ITK-60). At more than one thread ANTs' `-b` crashes (ANTS-60); LARMORX gives its one-thread result at any thread count.

First the blobs: in fMRIPrep's T1w of ds000005 both programs find the same 30 blobs, each drawn here as a sphere of its radius around its voxel (ANTs' from its own code, built with prints: `validation/probes/ants-ai-blobs`).

{{ ev.example('ants-ai', 'blobs-found') }}

Two copies of that T1w with a known transform show what the pairing and the landmark test do. The first is the same voxels with the origin moved: ANTs' test keeps ten pairs that are all exact and finds the translation exactly; LARMORX's default keeps the eleventh too, a fixed blob matched to a neighbouring moving blob 3 mm from where it should be, and its transform is up to 1.4 mm off. For a translation ANTs' test happens to be the stricter one; the tables list every pair, which program kept it, and how far each transform is from the truth.

{{ ev.example('ants-ai', 'blobs-shift') }}

The second is the T1w rotated by 8 degrees (in millimetres) and shifted: no pair keeps the length of its displacement, ANTs keeps no landmark, and its transform (and LARMORX's in `reproduce` mode, the same file) is NaN. LARMORX's default keeps the five pairs whose distances are preserved, leaves out the two that are 65 and 109 mm off, and finds a rotation of 8.5 degrees, within 1.4 mm of the truth.

{{ ev.example('ants-ai', 'blobs-rotated') }}

Between subjects, or to a template, the patch matching rarely pairs the same anatomy: on the five oracle runs' T1w against MNI152NLin2009cAsym (2 mm), neither keeps a landmark with 30 blobs (the [full tier](repo:docs/validation/ants-ai-full.md)'s `real/*/blobs-mni-rigid` cases). The blob alignment is a rough initialiser for images of one subject.

## Every case {#cases}

Each case of the two records, with what it tests, its verdict and the reason. Search, filter by category or verdict, sort by a column; `#case=<program>/<name>` links to one.

### antsAI {#list-antsAI}

{{ ev.cases('ants-ai', 'ai') }}

### antsAffineInitializer {#list-antsAffineInitializer}

{{ ev.cases('ants-ai', 'init') }}

## Speed {#speed}

No benchmark report yet: the benchmark of antsAI and antsAffineInitializer is pending.

## Known limits {#limits}

The expected divergences: where ANTs never finishes or crashes (an empty blob list, ANTS-115; `-b` at more than one thread, ANTS-60), LARMORX refuses or gives ANTs' one-thread result; where ANTs seeds its random sampling from the clock (ANTS-58), LARMORX is repeatable. Whether a blob patch may be compared reflected (ANTs does not check the sign of its rotation, and the gradients' axes have arbitrary signs: ANTS-116) is left as ANTs does it, for the user to decide.
