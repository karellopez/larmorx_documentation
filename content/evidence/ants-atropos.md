---
title: Atropos
kicker: Evidence · ANTs
lede: >-
  `Atropos` labels the voxels of a mask with a few classes, alternating between the classes'
  intensity models and the labelling, with a Markov random field (MRF). LARMORX's port is a
  replica of ANTs 2.6.5's program on ITK 5.4.5. In `reproduce` it gives ANTs' images bit for
  bit in every compared case of its two records once ANTs uses correctly rounded maths (58 of
  58 and 17 of 17). With ANTs as built, 27 of the 58 and 3 of the 17 match bit for bit, and the
  classified image matches in all of them; the others' posteriors differ only where glibc's
  `expf`, `logf`, `exp`, `log` or `pow` is not correctly rounded. sMRIPrep's own call, in five
  fMRIPrep runs, is among them. Its default, `fix`, corrects ITK-50 and nineteen other defects
  of ANTs and ITK, among them partial-volume classes that the MRF shut out (ANTS-106).
description: >-
  How LARMORX's replica of ANTs' Atropos compares with ANTs 2.6.5 and fMRIPrep 25.2.6:
  sMRIPrep's segmentation of a real T1w by ANTs at 1 to 8 threads and with the clock's seed, a
  segmentation with tissue priors, ITK-50 corrected, partial-volume classes with the MRF on a
  phantom of known fractions (ANTS-106 corrected), two brains of the data panel, and every case
  of the records with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: translated from ANTs 2.6.5's and ITK 5.4.5's source (Apache-2.0)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span>, with its data panel (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/ants-atropos.md') }}">standard comparison</a>, <a href="{{ repo('docs/validation/ants-atropos-full.md') }}">full comparison</a>, <a href="{{ repo('docs/validation/ants-atropos-panel.md') }}">data panel</a>, all against ANTs 2.6.5</dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/ants-atropos.md') }}">ants-atropos</a> · findings <a href="{{ repo('docs/findings/ants-atropos.md') }}">ants-atropos</a></dd>
</dl>

## What is compared {#what-it-is}

`Atropos` labels the voxels of a mask with a few classes (tissues), alternating between the classes' intensity models and the labelling: K-means, Otsu, random or prior-based initializations; Gaussian, Parzen-window and tensor likelihoods; an MRF prior updated by iterated conditional modes. sMRIPrep calls it once per subject, in its brain extraction, to split the brain into CSF, grey and white matter.

The replica runs beside ANTs 2.6.5's `Atropos` on the same files with the same arguments. ANTs is the repository's build (GCC 14.3), run as built and with correctly rounded maths, at one thread in the records and at more for its own variability; three times with the clock's seed, where its runs differ. fMRIPrep's own ANTs 2.6.2 runs too, in fMRIPrep's image.

```bash
larmorx ants Atropos -d 3 -a t1w_n4.nii.gz -x brain_mask.nii.gz -i 'KMeans[3]' -k Gaussian -m '[0.1,1x1x1]' -c '[3,0]' -r 0 -o '[labels.nii.gz,POSTERIOR_%02d.nii.gz]'
```

```python
import larmorx as lx

seg = lx.ants.atropos("t1w_n4.nii.gz", "brain_mask.nii.gz", classes=3, mrf_smoothing=0.1,
                      iterations=3, convergence_threshold=0, use_random_seed=False)
csf, gm, wm = seg.posteriors
```

The [API page](repo:docs/api/ants-atropos.md) maps every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its port {#ports}

ANTs and ITK come under the Apache-2.0 licence, as LARMORX does, so the replica is in `larmorx` itself. It is translated from ANTs' and ITK's source, step by step, to give their results bit for bit. A clean room of ANTs' programs is planned after FreeSurfer ([roadmap](/roadmap/)).

The replica computes the C library's maths correctly rounded, the same on every platform. Where glibc's `expf` and `logf` are not correctly rounded for a value a run meets, ANTs as built gives the same classified image and posteriors that differ in their last bits.

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-atropos', 'port') }}

In `reproduce`, every case that writes images gives ANTs' images bit for bit at one thread with correctly rounded maths, but one: Grubbs-Rosner from its second iteration, where ANTs weighs part of its samples with memory it never wrote (ANTS-107), so that its own result changes with the length of its output paths. Against ANTs as built the classified images are identical in every case, and the posteriors differ in their last bits where glibc's `expf` and `logf` are not correctly rounded. Where ANTs aborts or crashes, the replica prints ANTs' message and stops; where ANTs seeds from the clock, its runs differ from each other, and the replica uses a fixed seed.

## In sMRIPrep: a real T1w segmented {#example}

fMRIPrep's brain extraction segments the N4-corrected T1w into three classes. Its inputs and arguments go to ANTs at 1, 2, 4 and 8 threads, three times with the clock's seed, to fMRIPrep's own ANTs, and to the replica. Atropos does not depend on ANTs' thread count, and fMRIPrep's output is the repository's ANTs result; the replica differs from it only in the last bits of a few posteriors (glibc's maths). Its default, `fix`, corrects ITK-50, where ITK's k-means leaves out the k-d tree's split points: a change smaller than ANTs' own spread when it seeds from the clock, shown on the slice below.

{{ ev.example('ants-atropos', 'fmriprep-atropos') }}

## A segmentation with tissue priors {#priors}

The same T1w segmented as antsCorticalThickness segments one: OASIS30ANTs' CSF, cortical grey matter and white matter priors, brought into the T1w's space with the transform fMRIPrep computed, weigh 0.25 against the likelihoods.

{{ ev.example('ants-atropos', 'oasis-priors') }}

## Partial-volume classes with the MRF {#partial-volume}

With `--use-partial-volume-likelihoods 1`, Atropos adds a class for each pair of tissues given with `-s` (here 1x2 and 2x3), for the voxels that mix them. In ANTs' MRF a partial-volume label is +1 against every neighbour, its own two tissues included, while a tissue next to its own kind is −2. So with any MRF the partial-volume classes hardly win a voxel, and Atropos stops when one wins none ("2 non-zero label sets but 5 is requested"; sMRIPrep's MRF of 0.1 on a real T1w stops this way). The replica corrects it by default (ANTS-106): a partial-volume label counts as a member of its own set, −1 with its tissues, −2 with itself, +1 with any other label; `reproduce` keeps ANTs' energies. A phantom whose voxels' tissue fractions are known measures what the correction does.

{{ ev.example('ants-atropos', 'pv-phantom') }}

{{ ev.table('ants-atropos', 'ants-106') }}

## On the data panel {#data-panel}

The [data panel](/data-panel/) is the fixed set of fourteen OpenNeuro subjects on which LARMORX's programs are validated: 1.5, 3 and 7 T; Siemens, GE and Philips; single-band, multiband and multi-echo BOLD; a 3.5-year-old to an 82-year-old; a tumour, a stroke with its lesion mask, strong motion. Its record replays every call fMRIPrep 25.2.6 made of the program in its fourteen runs on these subjects, the node's own `command.txt` with its inputs from the run's working directory (calls repeated word for word are compared once), and runs the program on panel images fMRIPrep never gives it. ANTs runs at one thread, as built and with correctly rounded maths, and at 2 and 3 threads for its own variability where it has any; the replica in `reproduce`, and in `fix` for the corrections. The panel's cases are in the case explorer below (the categories *data panel: fMRIPrep's calls* and *data panel: other images*).

**17 of 17 bit-identical to ANTs with correctly rounded maths, the classes identical in all 17**: sMRIPrep's segmentation in the brain extraction of all fourteen runs, and three calls fMRIPrep never makes (the stroke outside its manual lesion mask, a child's T1w and T2w as two channels, a FLAIR of 3 mm slices). Against fMRIPrep's own files (ANTs 2.6.2 with glibc's maths) the segmentation is the same in every run, and the posteriors differ in their last bits in 0 to 4,175 voxels. The panel also found a check the replica lacked: an input on another grid (a mask written from the image's affine, its spacing 2.9e-6 mm off) makes ITK throw, and now the replica too (one more case, rejected by both).

{{ ev.table('ants-atropos', 'panel-nodes') }}

Images on a small grid (a BOLD reference, a template at 2 mm) are shown as whole volumes; the panel's large anatomical images (up to 17.5 million voxels) as three full-resolution slices through the voxel where the replica and ANTs as built differ most (the centre of the field of view where they agree), the whole field of view shown, defaced heads included (the data panel's defacing check).

{{ ev.example('ants-atropos', 'panel-tumour') }}

{{ ev.example('ants-atropos', 'panel-stroke') }}

## Every case {#cases}

Each case of the two records, the standard comparison and the data panel, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('ants-atropos') }}

## Corrections by default {#corrections}

Where ANTs has a deterministic defect that changes a result, the replica corrects it by default, `fix`, and warns. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives ANTs' behaviour, and the records compare with it. The record's list of what `fix` changed meets ITK-50, ITK-51 and ANTS-90 to ANTS-106, each corrected by default ([register](repo:docs/findings/upstream-defects.md)). ITK-50 changes sMRIPrep's own call, as the worked example measures; ANTS-106 changes partial-volume classes with an MRF, as the phantom above measures. ANTS-107, where ANTs weighs part of its samples with memory it never wrote, is not met by default and is filled deterministically when reproduced.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original and the replica, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a case of the record, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/ants-atropos/', 'ants-atropos') }}

## Known limits {#limits}

The comparison with ANTs is made on Linux x86-64, against ANTs at one thread. ANTs' clock-seeded runs have no single result to compare with: they are compared as one more draw. There is no benchmark report yet. The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output.

## History {#history}

- **2026-10-22**: ANTS-106 corrected by default, the partial-volume classes with an MRF (the user's decision), measured on the phantom of known fractions.
- **2026-10-23**: the records of the standard and full comparisons shown here.
- **2026-10-26**: the data panel's record, sMRIPrep's segmentation in all fourteen runs and three more calls.
