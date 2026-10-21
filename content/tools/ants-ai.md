---
title: antsAI and antsAffineInitializer
kicker: Tools · ANTs
lede: >-
  The initial alignments of a registration, ported from ANTs 2.6.5 and ITK 5.4.5: antsAI's
  principal axes and multi-start search (its blob alignment not yet), and
  antsAffineInitializer.
description: LARMORX's ports of antsAI and antsAffineInitializer, their validation against ANTs 2.6.5 in figures, and ANTs' own thread variability.
---

<dl class="facts">
<dt>Implementation</dt><dd>ports of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span> (each)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/ants-ai.md') }}">ants-ai</a> (<a href="{{ repo('docs/validation/ants-ai-full.md') }}">full</a>) · <a href="{{ repo('docs/validation/ants-affine-initializer.md') }}">ants-affine-initializer</a> (<a href="{{ repo('docs/validation/ants-affine-initializer-full.md') }}">full</a>) · API <a href="{{ repo('docs/api/ants-ai.md') }}">ants-ai</a>, <a href="{{ repo('docs/api/ants-affine-initializer.md') }}">ants-affine-initializer</a></dd>
</dl>

## What they are

Both find a starting transform for a registration: antsAI aligns centres, principal axes or moments and searches rotations and translations from many starting points against a metric (Mattes, GC, MI); antsAffineInitializer searches rotations about the principal axes. fMRIPrep's `init_aff` steps run antsAI before the brain extraction and the BOLD-to-T1w registration.

## How to call them

```bash
larmorx ants antsAI -d 3 -m Mattes[template.nii.gz,t1w.nii.gz,32,Regular,0.25] -x template_mask.nii.gz \
  -t Affine[0.1] -s [15,0.1] -g [40.0,0x40x40] -p 0 -c [10,1e-06,10] -o initialization.mat
larmorx ants antsAffineInitializer 3 fixed.nii.gz moving.nii.gz init.mat 15 0.1 0 10
```

In Python: `lx.ants.ai` and `lx.ants.affine_initializer`.

## Agreement with ANTs

antsAI's [record](repo:docs/validation/ants-ai.md) runs 102 cases: 52 pass, 46 are rejected by both programs (ANTs' messages and exit statuses compared) and 4 are expected divergences; of the 52 compared, 51 are identical to the unmodified ANTs (exit status, standard output and error, every file) and 1 once ANTs uses correctly rounded maths. On fMRIPrep's own transforms, made by ANTs 2.6.2 at 8 threads, LARMORX is within 1.6 × 10⁻¹³. antsAffineInitializer's [record](repo:docs/validation/ants-affine-initializer.md) runs 41 cases: 26 pass, all identical to the unmodified ANTs, 13 are rejected by both and 2 are expected divergences.

{{ figure('ants-ai/agreement-ai', "antsAI's 102 cases by category; the first bar splits the compared cases between identical to ANTs as built and identical with CORE-MATH.") }}

{{ figure('ants-ai/agreement-initializer', "antsAffineInitializer's 41 cases by category.") }}

## ANTs' own variability

{{ figure('ants-ai/thread-band', "The largest change in a transform parameter between ANTs at one thread and ANTs at 2, 4 and 8 threads, for the cases the two records measure (log scale). LARMORX gives the one-thread result at any thread count, identical to ANTs at one thread in these cases.") }}

## Speed

No benchmark report yet: the benchmark of antsAI and antsAffineInitializer is pending.

## Known limits

antsAI's blob alignment (`-b`) is not ported yet; it is its own task ([next steps](repo:docs/next-steps.md)). The expected divergences: where ANTs never finishes, LARMORX refuses; where ANTs seeds its random sampling from the clock (ANTS-58), LARMORX is repeatable.
