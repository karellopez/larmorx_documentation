---
title: Tools
kicker: Documentation
lede: One page per tool ported so far, with figures that compare it with the original program, drawn from its validation record.
description: The tools LARMORX implements today, each with figures comparing it with the original program (ANTs, AFNI, FSL, fMRIPrep, nibabel), drawn from the validation records.
---

Each page says what the tool is, how LARMORX implements it (a port of the source, a clean-room original, an exact replica) and how to call it, then shows its validation record in figures: how its cases agree with the original program, how its remaining differences compare with the original's own variability, what it does on real data, and its speed where a benchmark report exists. Every figure is drawn by the main repository's code from a committed record ([docs/figures.md](repo:docs/figures.md)), and its provenance is linked beneath it.

<ul class="tool-index">
{%- for t in site.tools %}
<li class="eco-{{ t.eco }}"><a href="{{ link(t.url) }}">{{ t.title }}</a><p>{{ t.summary }}</p></li>
{%- endfor %}
</ul>

## How to read the figures {#reading}

[N4BiasFieldCorrection](/tools/ants-n4/) and [3dTshift](/tools/afni-tshift/) show their validation as evidence to inspect: worked examples on real data in an image viewer, the metrics of every comparison, a verdict for every comparison and case, and every parity case in a searchable table ([how to read them](/validation/#reading)). The other pages follow; until then they show the figures below.

- **Agreement.** One bar per category of a record's cases, as shares of the category. *Identical* means the same bits as the unmodified original program; *identical with correctly rounded maths* means the same bits once the original's math library (glibc's `exp`, `log`, `sin`, `cos`, which are not always correctly rounded) is replaced by CORE-MATH's, which LARMORX uses on every platform; *within the thresholds* means the record's stated tolerance, not bit-identity; *rejected by both* means both programs refuse the input, compared by exit status and messages; *expected divergence* means a documented, deliberate difference.
- **Differences against the original's own variability.** Where an original's result depends on its thread count, the record measures that band, and the figures place LARMORX's differences next to it.
- **Images.** Brain slices only, masked to the brain, from OpenNeuro datasets in the public domain (PDDL-1.0, CC0-1.0) and the MNI ICBM 152 template ([notice](/static/hero/LICENSE-MNI.txt)); difference maps on a symmetric scale whose range is stated.
- **Speed.** Medians from the benchmark reports, on the machine they name. Where a tool has no benchmark report yet, its page says so.
