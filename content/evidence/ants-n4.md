---
title: N4BiasFieldCorrection
kicker: Evidence · ANTs
lede: >-
  `N4BiasFieldCorrection` estimates the smooth bias field that makes one tissue brighter in one
  part of an image than in another, and divides it out. LARMORX's port is a replica of ANTs
  2.6.5's program on ITK 5.4.5. In `reproduce` it gives ANTs' output bit for bit in every
  compared case of its two records once ANTs uses correctly rounded maths (46 of 46 and 69 of
  69). With ANTs as built, 29 of the 46 and 20 of the 69 match bit for bit; the others differ
  only where glibc's maths is not correctly rounded.
  On fMRIPrep's own N4 of a real T1w, on any number of threads, it gives ANTs' one-thread
  result with correctly rounded maths. Its default, `fix`, leaves the zero and negative voxels out of the fit
  (ANTS-40), a correction measured on fMRIPrep's 25 N4 calls.
description: >-
  How LARMORX's replica of ANTs' N4BiasFieldCorrection compares with ANTs 2.6.5 and fMRIPrep
  25.2.6: fMRIPrep's final N4 of a real T1w, the correction of zero and negative voxels (ANTS-40)
  on a 7 T template, six images of the data panel, ANTs' own variability between thread counts,
  every case of the two records with its verdict, random testing and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: translated from ANTs 2.6.5's and ITK 5.4.5's source (Apache-2.0)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span>, with its data panel (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/ants-n4.md') }}">standard comparison</a> (ANTs 2.6.5), <a href="{{ repo('docs/validation/ants-n4-panel.md') }}">data panel</a> (ANTs 2.6.5) · benchmark <a href="{{ repo('docs/benchmarks/ants-n4.md') }}">ants-n4</a> · findings <a href="{{ repo('docs/findings/ants-n4.md') }}">ants-n4</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/ants-n4.md') }}">ants-n4</a></dd>
</dl>

## What is compared {#what-it-is}

N4 estimates a smooth multiplicative bias field by fitting B-splines to the residual of a sharpened intensity histogram, level by level, and divides it out. fMRIPrep, sMRIPrep and sdcflows call it on BOLD references, T1w images (before the template and in the brain extraction) and field-map magnitudes.

The replica runs beside ANTs 2.6.5's `N4BiasFieldCorrection` on the same files with the same arguments. ANTs is the repository's build (GCC 14.3), run on one thread as built and with correctly rounded maths, and at more threads for its own variability. fMRIPrep's own ANTs 2.6.2 runs too, in fMRIPrep's image.

```bash
larmorx ants N4BiasFieldCorrection -d 3 -b '[200]' -c '[50x50x50x50x50,1e-7]' -s 4 -i t1w.nii.gz -o '[t1w_n4.nii.gz,bias.nii.gz]'
```

```python
import larmorx as lx

res = lx.ants.n4_bias_field_correction(
    "sub-01_T1w.nii.gz", shrink_factor=4,
    convergence=([50] * 5, 1e-7), bspline_fitting=200, n_threads=8,
)
corrected, bias = res.corrected, res.bias_field
```

The [API page](repo:docs/api/ants-n4.md) maps every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its port {#ports}

ANTs and ITK come under the Apache-2.0 licence, as LARMORX does, so the replica is in `larmorx` itself. It is translated from ANTs' and ITK's source, step by step, to give their results bit for bit. A clean room of ANTs' programs is planned after FreeSurfer ([roadmap](/roadmap/)).

ANTs' N4 changes with its thread count; the replica gives ANTs' single-thread result on any number of threads. It computes the C library's maths (`expf`, `logf`, `exp`, `sincos`) correctly rounded, the same on every platform, which is why ANTs as built differs from it in the last bits where glibc's are not.

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-n4', 'port') }}

In `reproduce`, every case that produces an image gives ANTs' output bit for bit: as ANTs is built (glibc's maths, one thread), or, where glibc's `expf`, `logf`, `exp` or `sincos` is not correctly rounded for a value the run meets, once the same ANTs binary uses CORE-MATH's correctly rounded functions. The invalid inputs are refused by both programs. One case, `inputs/zero-background-known`, checks ANTS-40's correction against ANTs' own field with a mask of the positive voxels (its verdict is the correction). Nothing is open.

## In fMRIPrep: the final N4 of a real T1w {#example}

The image viewer below holds the same N4 run by fMRIPrep 25.2.6, by its own ANTs at one thread, by the repository's ANTs 2.6.5 (as built, with correctly rounded maths, at 1 to 12 threads) and by the replica (1 and 12 threads, `reproduce` and `fix`). The replica's panels in `reproduce` give ANTs' result. In `fix`, the default, ANTS-40's correction leaves out the few zero voxels this call's weight image includes (the row *replica, fix − reproduce*). Choose the panels, the plane, the slice and the window; select a point to read every panel's exact value there; set two images side by side, swipe or blink between them.

{{ ev.example('ants-n4', 'final-n4') }}

## A deliberate correction: zero and negative voxels (ANTS-40) {#ants-40}

ITK's N4 takes the logarithm of the voxels it uses only where they are above 0: a 0 stays 0, the logarithm of an intensity of 1, and a negative value stays negative, far below every tissue's logarithm. Both enter the histogram N4 sharpens and the B-spline fit. fMRIPrep runs every N4 without a mask, so a zero background, zero-filled voxels and negative values are fitted as if they were tissue. The project's rules put such a defect to measurement first: every N4 call of the five fMRIPrep runs, run as ANTs does and with those voxels left out (what a mask of the positive voxels does, which a unit test of the replica shows to be the correction itself), against ANTs' own variability for the same call, and phantoms with a known bias field.

{{ ev.table('ants-n4', 'ants-40-calls') }}

Sixteen of the 25 calls use such voxels. Leaving them out changes the field far beyond ANTs' own variability, even for a handful of voxels among tens of thousands; on the phantoms it recovers the known field better, and on fMRIPrep's final N4s the white matter becomes more uniform in all five runs.

{{ ev.table('ants-n4', 'ants-40-phantoms') }}

The decision was to correct it by default: a value without a logarithm has no place in N4's model of the log intensities. The example is the run where it matters most: sMRIPrep's final N4 of a 7 T T1w template (ds005454 sub-16), which has negative values. Their logarithms stretch the histogram until the tissue sits in one or two of its bins, the sharpening changes nothing, and ANTs' bias field is flat: it corrects nothing. With them left out, the replica's `fix` corrects the image; `reproduce` gives ANTs' output.

{{ ev.example('ants-n4', 'ants-40') }}

## Against the original's own variability {#variability}

ANTs' N4 changes with its thread count ([ANTS-37](repo:docs/findings/upstream-defects.md)): ITK's B-spline fit sums per-thread lattices. The record measures that band for every case that differs from ANTs as built, and divides the replica's difference by it.

{{ ev.band('ants-n4') }}

## On the data panel {#data-panel}

The [data panel](/validation/data-panel/) is the fixed set of fourteen OpenNeuro subjects on which LARMORX's programs are validated: 1.5, 3 and 7 T; Siemens, GE and Philips; single-band, multiband and multi-echo BOLD; a 3.5-year-old to an 82-year-old; a tumour, a stroke with its lesion mask, strong motion. Its record replays every call fMRIPrep 25.2.6 made of the program in its fourteen runs on these subjects, the node's own `command.txt` with its inputs from the run's working directory (calls repeated word for word are compared once), and runs the program on panel images fMRIPrep never gives it. ANTs runs at one thread, as built and with correctly rounded maths, and at 2 and 3 threads for its own variability where it has any; the replica in `reproduce`, and in `fix` for the corrections. The panel's cases are in the case explorer below (the categories *data panel: fMRIPrep's calls* and *data panel: other images*).

**69 of 69 bit-identical to ANTs with correctly rounded maths, 20 to ANTs as built**: all 64 N4 calls of the fourteen runs (the BOLD references, the brain extraction's and the final anatomical corrections, the field maps' magnitudes) and sMRIPrep's final options on five images fMRIPrep never corrects (the 7 T MP2RAGE, a 3 T MP2RAGE UNIT1, the 82-year-old's FLAIR, a glioma's T2w of 6 mm slices, the stroke's T2w fitted outside its lesion). Against ANTs as built every difference is within 0.042 of ANTs' own difference between one thread and two or three. A mask written from the image's affine (2e-6 mm off its grid) is refused by both, as ITK's input check requires.

{{ ev.table('ants-n4', 'panel-nodes') }}

Images on a small grid (a BOLD reference, a template at 2 mm) are shown as whole volumes; the panel's large anatomical images (up to 17.5 million voxels) as three full-resolution slices through the voxel where the replica and ANTs as built differ most (the centre of the field of view where they agree), the whole field of view shown, defaced heads included (the data panel's defacing check).

{{ ev.example('ants-n4', 'panel-boldref-mb8') }}

{{ ev.example('ants-n4', 'panel-7t') }}

{{ ev.example('ants-n4', 'panel-tumour') }}

{{ ev.example('ants-n4', 'panel-flair') }}

{{ ev.example('ants-n4', 'panel-tumour-t2w') }}

{{ ev.example('ants-n4', 'panel-unit1') }}

## Every case {#cases}

Each case of the two records, the standard comparison and the data panel, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('ants-n4') }}

## Speed {#speed}

The wall time of the whole command on six command lines of fMRIPrep, sMRIPrep and sdcflows, from a BOLD reference to a raw T1w, with ANTs and the replica at 1 and 12 threads ([benchmark](repo:docs/benchmarks/ants-n4.md)).

{{ ev.speed('ants-n4') }}

## Corrections by default {#corrections}

Where ANTs has a deterministic defect that changes a result, the replica corrects it by default, `fix`, and warns. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives ANTs' behaviour, and the records compare with it. The record's list of what `fix` changed meets ANTS-35, ANTS-36, ANTS-38, ANTS-40 and ITK-02 ([register](repo:docs/findings/upstream-defects.md), [findings](repo:docs/findings/ants-n4.md)). Of them, ANTS-40 is the one measured on fMRIPrep's calls in the five runs (above); the measurement and its code are in the repository ([investigation](repo:validation/investigations/ants-40-n4-nonpositive/README.md)). Many of the data panel's calls pass `-r` without a mask (ANTS-36): the replica, like ANTs, does nothing with it in either mode, and warns. The panel's record names it in 36 cases. In the tumour example the values change through ANTS-40 alone.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original and the replica, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a case of the record, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/ants-n4/', 'ants-n4') }}

## Known limits {#limits}

The comparison with ANTs is made on Linux x86-64; the cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output. The ANTs it is compared with is built by GCC 14.3, which honours the source's float roundings; an older GCC 11 build of ANTs gives other bits ([findings](repo:docs/findings/ants-n4.md)).

## History {#history}

- **2026-10-12**: ANTS-35, ANTS-36, ANTS-38 and ITK-02 corrected by default ([register](repo:docs/findings/upstream-defects.md#summary)).
- **2026-10-23**: ANTS-40 measured on fMRIPrep's 25 N4 calls, as the project's rules for a defect of unknown effect require, and corrected by default.
- **2026-10-26**: the data panel's record, every N4 call of the fourteen runs and five more images.
