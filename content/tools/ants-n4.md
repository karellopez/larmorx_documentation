---
title: N4BiasFieldCorrection
kicker: Tools · ANTs
lede: Intensity non-uniformity correction, ported from ANTs 2.6.5 and ITK 5.4.5. In reproduce mode every case of its record is bit-identical to ANTs, as built or once ANTs uses correctly rounded maths; on fMRIPrep's own N4 of a real T1w it is ANTs at one thread with correctly rounded maths, at any thread count. By default LARMORX leaves the zero and negative voxels out of the fit (ANTS-40, measured on fMRIPrep's 25 N4 calls).
description: LARMORX's port of ANTs' N4BiasFieldCorrection, validated against ANTs 2.6.5 and fMRIPrep 25.2.6 — a worked example on a real T1w to inspect, every parity case with its verdict, ANTs' own variability, and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ANTs' and ITK's source (Apache-2.0), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/ants-n4.md') }}">ants-n4</a> · benchmark <a href="{{ repo('docs/benchmarks/ants-n4.md') }}">ants-n4</a> · API <a href="{{ repo('docs/api/ants-n4.md') }}">ants-n4</a> · findings <a href="{{ repo('docs/findings/ants-n4.md') }}">ants-n4</a></dd>
<dt>Data panel</dt><dd><a href="{{ repo('docs/validation/ants-n4-panel.md') }}">ants-n4-panel</a></dd>
</dl>

## What it is

N4 estimates a smooth multiplicative bias field by fitting B-splines to the residual of a sharpened intensity histogram, level by level, and divides it out. fMRIPrep, sMRIPrep and sdcflows call it on BOLD references, T1w images (before the template and in the brain extraction) and field-map magnitudes.

```bash
larmorx ants N4BiasFieldCorrection -d 3 -b [200] -c [50x50x50x50x50,1e-7] -s 4 -i t1w.nii.gz -o [t1w_n4.nii.gz,bias.nii.gz]
```

```python
import larmorx as lx

res = lx.ants.n4_bias_field_correction(
    "sub-01_T1w.nii.gz", shrink_factor=4,
    convergence=([50] * 5, 1e-7), bspline_fitting=200, n_threads=8,
)
corrected, bias = res.corrected, res.bias_field
```

The [API page](repo:docs/api/ants-n4.md) maps every option. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-n4', 'port') }}

Every case that produces an image is bit-identical to ANTs in reproduce mode: as built (glibc's maths, one thread), or, where glibc's `expf`, `logf`, `exp` or `sincos` is not correctly rounded for a value the run meets, once the same ANTs binary uses CORE-MATH's correctly rounded functions. The invalid inputs are refused by both programs. One case, `inputs/zero-background-known`, checks ANTS-40's correction against ANTs' own field with a mask of the positive voxels (its verdict is the correction). Nothing is open.

## A worked example: fMRIPrep's own N4 {#example}

The image viewer below holds the same N4 run by fMRIPrep 25.2.6, by its own ANTs at one thread, by the repository's ANTs 2.6.5 (as built, with correctly rounded maths, at 1 to 12 threads) and by LARMORX (1 and 12 threads, reproduce and default modes). The *larmorx* panels are reproduce mode, ANTs' result; *larmorx-fix* is the default, where ANTS-40's correction leaves out the few zero voxels this call's weight image includes (the row *larmorx default mode − reproduce mode*). Choose the panels, the plane, the slice and the window; select a point to read every panel's exact value there; set two images side by side, swipe or blink between them.

{{ ev.example('ants-n4', 'final-n4') }}

## A deliberate correction: zero and negative voxels (ANTS-40) {#ants-40}

ITK's N4 takes the logarithm of the voxels it uses only where they are above 0: a 0 stays 0, the logarithm of an intensity of 1, and a negative value stays negative, far below every tissue's logarithm. Both enter the histogram N4 sharpens and the B-spline fit. fMRIPrep runs every N4 without a mask, so a zero background, zero-filled voxels and negative values are fitted as if they were tissue. The project's rules put this to measurement first (2026-10-23): every N4 call of the five fMRIPrep oracle runs, run as ANTs does and with those voxels left out (what a mask of the positive voxels does, which LARMORX's unit test shows to be the correction itself), against ANTs' own variability for the same call, and phantoms with a known bias field.

{{ ev.table('ants-n4', 'ants-40-calls') }}

Sixteen of the 25 calls use such voxels. Leaving them out changes the field far beyond ANTs' own variability, even for a handful of voxels among tens of thousands; on the phantoms it recovers the known field better, and on fMRIPrep's final N4s the white matter becomes more uniform in all five runs.

{{ ev.table('ants-n4', 'ants-40-phantoms') }}

The decision was to correct it by default: a value without a logarithm has no place in N4's model of the log intensities. The example is the run where it matters most: sMRIPrep's final N4 of a 7T T1w template (ds005454 sub-16), which has negative values. Their logarithms stretch the histogram until the tissue sits in one or two of its bins, the sharpening changes nothing, and ANTs' bias field is flat: it corrects nothing. With them left out, LARMORX corrects the image; reproduce mode gives ANTs' output.

{{ ev.example('ants-n4', 'ants-40') }}

## Against ANTs' own variability {#variability}

ANTs' N4 changes with its thread count ([ANTS-37](repo:docs/findings/upstream-defects.md)): ITK's B-spline fit sums per-thread lattices. The record measures that band for every case that differs from ANTs as built, and divides larmorx's difference by it.

{{ ev.band('ants-n4') }}

## On the data panel {#data-panel}

The [data panel](/data-panel/) is the fixed set of fourteen OpenNeuro subjects every tool of LARMORX is validated on: 1.5, 3 and 7 T; Siemens, GE and Philips; single-band, multiband and multi-echo BOLD; a 3.5-year-old to an 82-year-old; a tumour, a stroke with its lesion mask, strong motion. Each record of the panel tier replays every call fMRIPrep 25.2.6 made of the program in its fourteen oracle runs, the node's own `command.txt` with its inputs from the run's working directory (calls repeated word for word are compared once), and runs the program on panel images fMRIPrep never gives it. ANTs runs at one thread, as built and with correctly rounded maths, and at 2 and 3 threads for its own variability where it has any; LARMORX in reproduce mode, and in its default mode for the corrections. The panel's cases are in the case explorers below (categories `panel-fmriprep` and `panel-images`).

**69 of 69 bit-identical to ANTs with correctly rounded maths, 20 to ANTs as built**: all 64 N4 calls of the fourteen runs (the BOLD references, the brain extraction's and the final anatomical corrections, the field maps' magnitudes) and sMRIPrep's final options on five images fMRIPrep never corrects (the 7 T MP2RAGE, a 3 T MP2RAGE UNIT1, the 82-year-old's FLAIR, a glioma's T2w of 6 mm slices, the stroke's T2w fitted outside its lesion). Against ANTs as built every difference is within 0.042 of ANTs' own difference between one thread and two or three. A mask written from the image's affine (2e-6 mm off its grid) is refused by both, as ITK's input check requires.

{{ ev.table('ants-n4', 'panel-nodes') }}

Images on a small grid (a BOLD reference, a template at 2 mm) are shown as whole volumes; the panel's large anatomical images (up to 17.5 million voxels) as three full-resolution slices through the voxel where LARMORX and ANTs as built differ most (the centre of the field of view where they agree), the whole field of view shown, defaced heads included (the data panel's defacing check).

{{ ev.example('ants-n4', 'panel-boldref-mb8') }}

{{ ev.example('ants-n4', 'panel-7t') }}

{{ ev.example('ants-n4', 'panel-tumour') }}

{{ ev.example('ants-n4', 'panel-flair') }}

{{ ev.example('ants-n4', 'panel-tumour-t2w') }}

{{ ev.example('ants-n4', 'panel-unit1') }}

## Every case {#cases}

Each case of the record, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('ants-n4') }}

## Speed {#speed}

{{ ev.speed('ants-n4') }}

## Corrections by default {#corrections}

Where ANTs has a deterministic defect that changes a result, LARMORX corrects it by default and warns; `upstream_defects="reproduce"` (or `LARMORX_UPSTREAM_DEFECTS=reproduce`) gives ANTs' behaviour, and the record compares in that mode. Its fix pass meets ANTS-35, ANTS-36, ANTS-38, ANTS-40 and ITK-02 ([register](repo:docs/findings/upstream-defects.md), [findings](repo:docs/findings/ants-n4.md)). Of them only ANTS-40 applies to fMRIPrep's calls (above); the measurement and its code are in the repository ([investigation](repo:validation/investigations/ants-40-n4-nonpositive/README.md)).

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/ants-n4/') }}

## Known limits {#limits}

The comparison with ANTs is made on Linux x86-64; the other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). ANTs' oracle is built by GCC 14.3, which honours the source's float roundings; an older GCC 11 build of ANTs gives other bits ([findings](repo:docs/findings/ants-n4.md)).
