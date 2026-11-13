---
title: antsApplyTransforms
kicker: Evidence · ANTs
lede: >-
  `antsApplyTransforms` resamples an image through a chain of ITK transforms, in double
  precision or with `--float 1`, and writes transforms too. LARMORX's port is a replica of ANTs
  2.6.5's program on ITK 5.4.5. In `reproduce` it gives ANTs' output data bit for bit in every
  compared case of its two records once ANTs uses correctly rounded maths (200 of 200 and 425
  of 425). With ANTs as built, 185 of the 200 and 329 of the 425 match bit for bit; the others
  differ only where glibc's `exp`, `log`, `sin` or `cos` is not correctly rounded. With `--float 1`, as fMRIPrep runs many of its calls, every case gives
  ANTs' data as built (102 of 102 and 167 of 167), and fMRIPrep's own T1w-to-MNI resampling
  bit for bit. The transforms it writes are ANTs' files (34 of 34).
description: >-
  How LARMORX's replica of ANTs' antsApplyTransforms compares with ANTs 2.6.5 and fMRIPrep
  25.2.6: fMRIPrep's T1w-to-MNI resampling through its .h5 composite, in single and double
  precision, a B-spline transform, three images of the data panel, every case of the two
  records with its verdict, random testing and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: translated from ANTs 2.6.5's and ITK 5.4.5's source (Apache-2.0)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span>, with its data panel (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/ants-apply-transforms.md') }}">standard comparison</a> (ANTs 2.6.5), <a href="{{ repo('docs/validation/ants-apply-transforms-panel.md') }}">data panel</a> (ANTs 2.6.5) · benchmark <a href="{{ repo('docs/benchmarks/ants-apply-transforms.md') }}">ants-apply-transforms</a></dd>
<dt>Reference</dt><dd><a href="{{ link('/programs/ants/antsApplyTransforms/') }}"><code>antsApplyTransforms</code></a> · API page <a href="{{ repo('docs/api/ants-apply-transforms.md') }}">ants-apply-transforms</a></dd>
</dl>

## What is compared {#what-it-is}

`antsApplyTransforms` maps every voxel of a reference grid through a list of transforms (matrices, displacement fields, B-spline transforms, composite `.h5` files) into an input image and interpolates it there: linear, nearest neighbour, B-spline, Gaussian, windowed sinc, label-preserving. fMRIPrep uses it for every resampling of its anatomical outputs and masks, many of them with `--float 1`.

The replica runs beside ANTs 2.6.5's `antsApplyTransforms` on the same files with the same arguments. ANTs is the repository's build (GCC 14.3), run as built and with correctly rounded maths: at 4 threads in the records, at 1 and 8 in the worked examples; its thread count changes nothing in this program, which resamples each voxel on its own. fMRIPrep's own ANTs 2.6.2 runs too, in fMRIPrep's image.

```bash
larmorx ants antsApplyTransforms -d 3 --float 1 -i sub-01_desc-preproc_T1w.nii.gz -r tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz -t sub-01_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5 -n LanczosWindowedSinc -o t1w_mni.nii.gz
```

```python
import larmorx as lx

mni = lx.ants.apply_transforms(
    "sub-01_desc-preproc_T1w.nii.gz",
    "tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz",
    ["sub-01_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5"],
    interpolation="lanczos", n_threads=8,
)
```

The [API page](repo:docs/api/ants-apply-transforms.md) maps every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its port {#ports}

ANTs and ITK come under the Apache-2.0 licence, as LARMORX does, so the replica is in `larmorx` itself. It is translated from ANTs' and ITK's source, step by step, to give their results bit for bit. A clean room of ANTs' programs is planned after FreeSurfer ([roadmap](/roadmap/)).

The replica computes the C library's maths (`exp`, `log`, `sin`, `cos`) correctly rounded, the same on every platform, which is why ANTs as built differs from it in the last bits where glibc's are not: the Gaussian and windowed-sinc weights, the Euler and versor matrices.

## The verdicts at a glance {#verdicts}

{{ ev.agreement('ants-apply-transforms', 'port') }}

In `reproduce`, image outputs give the unmodified ANTs binary's data bit for bit, or, where glibc's `exp`, `log`, `sin` or `cos` is not correctly rounded (Gaussian and windowed-sinc weights, Euler and versor matrices), the same binary's with CORE-MATH preloaded. Every `--float 1` case gives ANTs' data as built. The cases that write transforms (`-o Linear[...]`, `CompositeTransform[...]`, `DisplacementField[...]`) write ANTs' content: text and MATLAB files byte for byte, NIfTI fields bit for bit, HDF5 files dataset for dataset and attribute for attribute (their compressed bytes are ITK's given ITK's chunks). The four expected divergences are crashes of ANTs that the replica refuses with a message.

## In fMRIPrep: the T1w in MNI space {#example}

The node that writes fMRIPrep's `space-MNI152NLin2009cAsym_res-2_desc-preproc_T1w`: its masked T1w, the 2 mm template and its own composite transform (the affine and the SyN displacement field of its template registration), with Lanczos interpolation. fMRIPrep runs it with `--float 1`; double precision is shown beside it, where glibc's maths reaches the last bits. Choose the panels, the plane, the slice and the window; select a point to read every panel's exact value there; set two images side by side, swipe or blink between them.

{{ ev.example('ants-apply-transforms', 'fmriprep-anat2std') }}

## A B-spline transform {#bspline}

The output of `antsRegistration`'s `BSpline` stage: a cubic B-spline transform, here the one ANTs 2.6.5 found for the same T1w (sMRIPrep's template registration with `BSpline[0.1,104]` in place of its SyN stage, on every third voxel), applied with the registration's affine to the 1 mm T1w onto the 2 mm template, Lanczos, in single and double precision. *Swipe* sets the T1w through the affine alone against it through the B-spline transform too.

Why 104 mm and not antsRegistrationSyN.sh's 26 mm: the mesh doubles at each level, to about a million parameters at the last one, and ANTs computes every parameter's Jacobian at every voxel. With 26 mm ANTs had not finished after almost four hours at 4 threads; LARMORX's replica of `antsRegistration`, which computes only the 64 control points around each voxel, ran the same registration in 38 s at one thread ([findings](repo:docs/findings/ants-bspline.md)).

{{ ev.example('ants-apply-transforms', 'bspline-transform') }}

## On the data panel {#data-panel}

The [data panel](/validation/data-panel/) is the fixed set of fourteen OpenNeuro subjects on which LARMORX's programs are validated: 1.5, 3 and 7 T; Siemens, GE and Philips; single-band, multiband and multi-echo BOLD; a 3.5-year-old to an 82-year-old; a tumour, a stroke with its lesion mask, strong motion. Its record replays every call fMRIPrep 25.2.6 made of the program in its fourteen runs on these subjects, the node's own `command.txt` with its inputs from the run's working directory (calls repeated word for word are compared once), and runs the program on panel images fMRIPrep never gives it. ANTs runs at 4 threads, as built and with correctly rounded maths; the replica in `reproduce`, and in `fix` for the corrections. The panel's cases are in the case explorer below (the categories *data panel: fMRIPrep's calls* and *data panel: other images*).

**425 of 425 bit-identical to ANTs with correctly rounded maths, 329 to ANTs as built**: every `antsApplyTransforms` node of the fourteen runs (421 calls; 179 through fMRIPrep's `.h5` composites, 166 with `--float 1`; Gaussian, MultiLabel, windowed sinc, linear and nearest-neighbour interpolation) and four calls fMRIPrep never makes (the 600-volume multiband-8 series onto the T1w, the raw 7 T MP2RAGE and the stroke's lesion mask to MNI, the 82-year-old's FLAIR onto its T1w). The others differ only where ITK calls glibc's `exp`, `log`, `sin` or `cos`.

{{ ev.table('ants-apply-transforms', 'panel-nodes') }}

Images on a small grid (a BOLD reference, a template at 2 mm) are shown as whole volumes; the panel's large anatomical images (up to 17.5 million voxels) as three full-resolution slices through the voxel where the replica and ANTs as built differ most (the centre of the field of view where they agree), the whole field of view shown, defaced heads included (the data panel's defacing check).

{{ ev.example('ants-apply-transforms', 'panel-7t-to-mni') }}

{{ ev.example('ants-apply-transforms', 'panel-lesion-to-mni') }}

{{ ev.example('ants-apply-transforms', 'panel-flair-to-t1w') }}

## Every case {#cases}

Each case of the two records, the standard comparison and the data panel, with what it tests, the command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('ants-apply-transforms') }}

## Speed {#speed}

The wall time of the whole command on six of fMRIPrep's resampling jobs on ds000005 sub-01, from a BOLD reference onto the T1w to a 240-volume BOLD series, with ANTs (through ANTsPy) and the replica at 1 and 12 threads, both in double precision: the [benchmark](repo:docs/benchmarks/ants-apply-transforms.md) predates `--float 1`.

{{ ev.speed('ants-apply-transforms') }}

## Corrections by default {#corrections}

Where ANTs has a deterministic defect that changes a result, the replica corrects it by default, `fix`, and warns. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives ANTs' behaviour, and the records compare with it. The record's list of what `fix` changed meets ANTS-06 (undefined float-to-integer conversions of `-u char` and `-u uchar` outputs, clamped by default; [register](repo:docs/findings/upstream-defects.md)). It does not apply to fMRIPrep's commands.

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original and the replica, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a case of the record, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/evidence/ants-apply-transforms/', 'ants-apply-transforms') }}

## Known limits {#limits}

MINC transform files are refused with a message. A B-spline transform has no inverse: `-t [BSpline.txt,1]` fails, as in ANTs. The comparison with ANTs is made on Linux x86-64; the cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output.

## History {#history}

- **2026-10-23**: B-spline transform files read and applied, with `antsRegistration`'s `BSpline` stage; before, the replica refused them.
- **2026-10-26**: the data panel's record, every `antsApplyTransforms` node of the fourteen runs and four more calls.
