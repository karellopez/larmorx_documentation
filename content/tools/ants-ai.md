---
title: antsAI and antsAffineInitializer
kicker: Tools · ANTs
lede: >-
  The initial alignments of a registration, ported from ANTs 2.6.5 and ITK 5.4.5: antsAI's
  principal axes and multi-start search (its blob alignment not yet), and
  antsAffineInitializer. Every compared case is identical to ANTs, as built or with correctly
  rounded maths; on fMRIPrep's own brain extraction, LARMORX finds ANTs' one-thread transform.
description: LARMORX's ports of antsAI and antsAffineInitializer, validated against ANTs 2.6.5 and fMRIPrep 25.2.6 — the initial transform of sMRIPrep's brain extraction to inspect, as parameters, placed images and distances in mm, and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>ports of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span> (each)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/ants-ai.md') }}">ants-ai</a> (<a href="{{ repo('docs/validation/ants-ai-full.md') }}">full</a>) · <a href="{{ repo('docs/validation/ants-affine-initializer.md') }}">ants-affine-initializer</a> (<a href="{{ repo('docs/validation/ants-affine-initializer-full.md') }}">full</a>) · API <a href="{{ repo('docs/api/ants-ai.md') }}">ants-ai</a>, <a href="{{ repo('docs/api/ants-affine-initializer.md') }}">ants-affine-initializer</a></dd>
</dl>

## What they are

Both find a starting transform for a registration: antsAI aligns centres, principal axes or moments and searches rotations and translations from many starting points against a metric (Mattes, GC, MI); antsAffineInitializer searches rotations about the principal axes. fMRIPrep's `init_aff` steps run antsAI before the brain extraction and the BOLD-to-T1w registration.

```bash
larmorx ants antsAI -d 3 -m Mattes[template.nii.gz,t1w.nii.gz,32,Regular,0.25] -x template_mask.nii.gz \
  -t Affine[0.1] -s [15,0.1] -g [40.0,0x40x40] -p 0 -c [10,1e-06,10] -o initialization.mat
larmorx ants antsAffineInitializer 3 fixed.nii.gz moving.nii.gz init.mat 15 0.1 0 10
```

In Python: `lx.ants.ai` and `lx.ants.affine_initializer`. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-ai', 'ai') }}

{{ ev.agreement('ants-ai', 'init') }}

Every compared case gives ANTs' exit status, standard output, standard error and transform file, byte for byte, against the unmodified binary at one thread or, where glibc's maths is not correctly rounded, against the same binary with CORE-MATH preloaded. Where ANTs never finishes or seeds its sampling from the clock, LARMORX refuses or is repeatable (expected divergences).

## A worked example: the brain extraction's initial transform {#example}

fMRIPrep's `init_aff`, with its arguments, inputs and seed, and niworkflows' antsAffineInitializer call on the same two images. A transform is shown three ways: the T1w it places on the template (select *Checkerboard* under *Compare* to overlay the template and a placed T1w), its parameters, and how far two transforms send the template's brain apart, in mm.

{{ ev.example('ants-ai', 'init-aff') }}

## Every case {#cases}

Each case of the two records, with what it tests, its verdict and the reason. Search, filter by category or verdict, sort by a column; `#case=<program>/<name>` links to one.

### antsAI {#list-antsAI}

{{ ev.cases('ants-ai', 'ai') }}

### antsAffineInitializer {#list-antsAffineInitializer}

{{ ev.cases('ants-ai', 'init') }}

## Speed {#speed}

No benchmark report yet: the benchmark of antsAI and antsAffineInitializer is pending.

## Known limits {#limits}

antsAI's blob alignment (`-b`) is not ported yet; it is its own task ([next steps](repo:docs/next-steps.md)). The expected divergences: where ANTs never finishes, LARMORX refuses; where ANTs seeds its random sampling from the clock (ANTS-58), LARMORX is repeatable.
