---
title: Atropos
kicker: Tools · ANTs
lede: ANTs' finite-mixture segmentation with a Markov random field, ported from ANTs 2.6.5 and ITK. sMRIPrep's call is reproduced bit for bit with correctly rounded maths on all five oracle runs; ITK-50 and nineteen other defects of ANTs and ITK are corrected by default, among them partial-volume classes that the MRF shut out (ANTS-106).
description: LARMORX's port of ANTs' Atropos, validated against ANTs 2.6.5 and fMRIPrep 25.2.6 — sMRIPrep's segmentation of a real T1w to inspect, ANTs at 1 to 8 threads and with the clock's seed, a segmentation with tissue priors, ITK-50 corrected, partial-volume classes with the MRF on a phantom of known fractions (ANTS-106 corrected), and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ANTs' and ITK's source, in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/ants-atropos.md') }}">ants-atropos</a> · full tier <a href="{{ repo('docs/validation/ants-atropos-full.md') }}">ants-atropos-full</a> · API <a href="{{ repo('docs/api/ants-atropos.md') }}">ants-atropos</a> · findings <a href="{{ repo('docs/findings/ants-atropos.md') }}">ants-atropos</a></dd>
</dl>

## What it is

Atropos labels the voxels of a mask with a few classes (tissues), alternating between the classes' intensity models and the labelling: K-means, Otsu, random or prior-based initializations; Gaussian, Parzen-window and tensor likelihoods; an MRF prior updated by iterated conditional modes. sMRIPrep calls it once per subject, in its brain extraction, to split the brain into CSF, grey and white matter.

```bash
larmorx ants Atropos -d 3 -a t1w_n4.nii.gz -x brain_mask.nii.gz -i KMeans[3] -k Gaussian \
    -m [0.1,1x1x1] -c [3,0] -r 0 -o [labels.nii.gz,POSTERIOR_%02d.nii.gz]
```

```python
import larmorx as lx

seg = lx.ants.atropos("t1w_n4.nii.gz", "brain_mask.nii.gz", classes=3, mrf_smoothing=0.1,
                      iterations=3, convergence_threshold=0, use_random_seed=False)
csf, gm, wm = seg.posteriors
```

How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-atropos', 'port') }}

Every case that writes images is bit-identical to ANTs at one thread with correctly rounded maths, but one: Grubbs-Rosner from its second iteration, where ANTs weighs part of its samples with memory it never wrote (ANTS-107), so that its own result changes with the length of its output paths. Against ANTs as built the classified images are identical in every case, and the posteriors differ in their last bits where glibc's `expf` and `logf` are not correctly rounded. Where ANTs aborts or crashes, LARMORX prints ANTs' message and stops; where ANTs seeds from the clock, its runs differ from each other, and LARMORX uses a fixed seed.

## A worked example: sMRIPrep's segmentation {#example}

fMRIPrep's brain extraction segments the N4-corrected T1w into three classes, with its own arguments, by ANTs at 1, 2, 4 and 8 threads, three times with the clock's seed, by fMRIPrep's own ANTs, and by LARMORX. Atropos does not depend on ANTs' thread count, and fMRIPrep's output is the repository's ANTs result; LARMORX differs from it only in the last bits of a few posteriors (glibc's maths). Its default mode corrects ITK-50, where ITK's k-means leaves out the k-d tree's split points: a change smaller than ANTs' own spread when it seeds from the clock, shown on the slice below.

{{ ev.example('ants-atropos', 'fmriprep-atropos') }}

## A segmentation with tissue priors {#priors}

The same T1w segmented as antsCorticalThickness segments one: OASIS30ANTs' CSF, cortical grey matter and white matter priors, brought into the T1w's space with the transform fMRIPrep computed, weigh 0.25 against the likelihoods.

{{ ev.example('ants-atropos', 'oasis-priors') }}

## Partial-volume classes with the MRF {#partial-volume}

With `--use-partial-volume-likelihoods 1`, Atropos adds a class for each pair of tissues given with `-s` (here 1x2 and 2x3), for the voxels that mix them. In ANTs' MRF a partial-volume label is +1 against every neighbour, its own two tissues included, while a tissue next to its own kind is −2: with any MRF the partial-volume classes hardly win a voxel, and Atropos stops when one wins none ("2 non-zero label sets but 5 is requested"; sMRIPrep's MRF of 0.1 on a real T1w stops this way). The user decided on 2026-10-22 to correct it by default: a partial-volume label counts as a member of its own set, −1 with its tissues, −2 with itself, +1 with any other label; `reproduce` keeps ANTs' energies. A phantom whose voxels' tissue fractions are known measures what the correction does.

{{ ev.example('ants-atropos', 'pv-phantom') }}

{{ ev.table('ants-atropos', 'ants-106') }}

## Every case {#cases}

Each case of the record, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('ants-atropos') }}

## Corrections by default {#corrections}

The record's fix pass meets ITK-50, ITK-51 and ANTS-90 to ANTS-106, each corrected by default with `upstream_defects="reproduce"` (or `LARMORX_UPSTREAM_DEFECTS=reproduce`) giving ANTs' behaviour ([register](repo:docs/findings/upstream-defects.md)). ITK-50 changes sMRIPrep's own call, as the worked example measures; ANTS-106 changes partial-volume classes with an MRF, as the phantom above measures. ANTS-107, where ANTs weighs part of its samples with memory it never wrote, is not met by default and is filled deterministically when reproduced.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, a night at a time: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest night:

{{ ev.random_testing('/tools/ants-atropos/') }}

## Known limits {#limits}

The comparison with ANTs is made on Linux x86-64, against ANTs at one thread. ANTs' clock-seeded runs have no single result to compare with: they are compared as one more draw. There is no benchmark report yet. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md).
