---
title: FLIRT
kicker: Tools · FSL
lede: >-
  FSL's linear registration (flirt) and its matrix tool (convert_xfm), with the boundary-based
  registration fMRIPrep uses to align every BOLD run to the T1w: an exact replica of FSL
  6.0.7.23's source in the separate larmorx-nc package (the FSL Licence's non-commercial terms),
  experimental, which gives FSL's matrices and images bit for bit in every compared case of its
  record, fMRIPrep's own calls included. The clean-room original is still to be written.
description: LARMORX's FSL FLIRT (flirt, convert_xfm), an exact replica validated against FSL 6.0.7.23 — fMRIPrep's boundary-based registration of a real BOLD reference with the white-matter boundary it fits, a default 12-dof registration, -applyxfm on a raw BOLD series, two data-panel runs, the matrices as text with fMRIPrep's own, and every parity case of the record with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-nc</code>, under the FSL Licence's terms, run as a separate program), translated from FSL 6.0.7.23's source (fsl-flirt 2111.4); clean-room original (<code>larmorx</code>, Apache-2.0): planned, to be written from <a href="{{ repo('specs/flirt.md') }}">specs/flirt.md</a></dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span> (replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/fsl-flirt-replica.md') }}">fsl-flirt-replica</a> (standard tier, FSL 6.0.7.23) · API <a href="{{ repo('docs/api/fsl-flirt.md') }}">fsl-flirt</a></dd>
</dl>

## What it is

FLIRT finds the affine matrix that best aligns an input image to a reference: a cost function compares the two images under a candidate matrix (the correlation ratio by default; mutual information, normalised correlation, least squares and others on request), a search over rotations on a coarse grid finds the basin, and Powell's method refines it over a pyramid of blurred and subsampled copies, from 8 mm to the images' own resolution, by the steps of a schedule. The boundary-based cost (`-cost bbr`) instead samples the input's intensity on both sides of a white-matter surface taken from a segmentation of the reference (`-wmseg`), and rewards a contrast across it: the registration fMRIPrep relies on to put each BOLD run on its T1w. `-applyxfm` applies a given matrix, `convert_xfm` inverts, concatenates and decomposes matrices.

fMRIPrep calls it once per BOLD run, in its boundary-based registration (`bold_reg_wf/fsl_bbr_wf/flt_bbr`), after mri_coreg's initial alignment: `flirt -in <boldref> -ref <T1w brain> -wmseg <white matter> -init <initial matrix> -schedule $FSLDIR/etc/flirtsch/bbr.sch -dof 6 -searchcost bbr -basescale 1`.

```bash
larmorx fsl flirt -in boldref.nii.gz -ref T1w_brain.nii.gz -dof 6 -cost bbr \
    -wmseg wm.nii.gz -init init.mat -schedule bbr.sch -omat bold2t1.mat -out bold_in_t1
larmorx fsl convert_xfm -omat t12bold.mat -inverse bold2t1.mat
```

```python
import larmorx as lx

r = lx.fsl.flirt("boldref.nii.gz", "T1w_brain.nii.gz", init="init.mat", cost="bbr",
                 search_cost="bbr", dof=6, base_scale=1, schedule="bbr.sch",
                 wm_seg="wm_mask.nii.gz")
r.matrix          # the 4 × 4 matrix, as -omat writes it
r.image           # the BOLD reference on the T1w's grid
```

FSL is distributed under the FSL Licence, which allows non-commercial use only, so LARMORX keeps its FSL tools in two implementations: the exact replica translated from FSL's source, in the separate package `larmorx-nc` (`pip install larmorx-nc`), and a clean-room original in LARMORX itself, written from a behavioural specification without FSL's code. For FLIRT only the replica exists so far: `implementation="auto"` (and `larmorx fsl flirt`) runs it when `larmorx-nc` is installed, and a clear error names the package otherwise. The replica follows FSL 6.0.7.23, runs none of FSL's programs and needs no FSL installation; its FSL libraries (newimage, its cost functions, the matrix arithmetic of Armadillo 14.2.1 on OpenBLAS's LAPACK) are those every FSL replica of `larmorx-nc` shares with mcflirt and BET. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes: every file FSL writes (the matrix as text, the registered image's header and data), its exit status and its messages.

{{ ev.agreement('fsl-flirt', 'replica') }}

The record runs 141 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-flirt-replica.md)): 107 give FSL's files byte for byte, and in the other 34 FSL refuses the input and the replica refuses it alike, with the same message and exit status (*rejected by both*). They cover fMRIPrep's boundary-based calls on three oracle runs (a young adult, the data panel's 82-year-old and its three-year-old; the matrices also fMRIPrep's own, as text), every cost function with and without weights, the degrees of freedom, the search options, every interpolation and output data type, every schedule FSL ships and written ones that use every command of the schedule language, `-applyxfm` and `-applyisoxfm` on 3D and 4D images, the boundary-based options (its types, slope, given coordinates and normals, a field map), the 2D mode, and every error of the command line; `convert_xfm` with every option. Each case also runs the replica's default mode, where LARMORX corrects FSL's deterministic defects and names them; on these cases it changes nothing. Random testing's first trial (3,945 random calls on small synthetic images) found two kinds of difference, both fixed and kept as cases of the record; what it found beyond them is being worked through ([findings](repo:docs/validation/difftest.md)).

## In fMRIPrep: the boundary-based registration of a BOLD reference {#example}

fMRIPrep's own call on one of its oracle runs, given to FSL 6.0.7.23 and to the replica in its reproduce and default modes (and at one thread: the replica's parallel steps give the same values at any thread count). Choose the panels: the T1w (the reference), the white-matter mask drawn over the BOLD reference at the initial alignment and over FSL's result (the boundary the cost aligns the BOLD contrast to), FSL's registered image and the replica's. The difference *FSL's result − its initial alignment* shows what the registration changed; the replica's differences from FSL are zero. Below the viewer, the matrices as the files hold them, and the displacement each pair gives over the brain.

{{ ev.example('fsl-flirt', 'fmriprep-bbr') }}

## A default registration {#dof12}

FLIRT without options beyond its inputs: 12 degrees of freedom, the correlation ratio, the search over rotations and the default schedule, registering the same BOLD reference to the T1w at half resolution (the record's case `real/default`).

{{ ev.example('fsl-flirt', 'dof12') }}

## `-applyxfm` on a raw BOLD series {#applyxfm}

A given matrix applied to four volumes of the raw BOLD series with windowed-sinc interpolation, onto the T1w's grid (the record's case `real/applyxfm-4d`): the resampling part of FLIRT, with its blur of the input where the output grid is coarser.

{{ ev.example('fsl-flirt', 'applyxfm-4d') }}

## On the data panel: an 82-year-old and a three-year-old {#panel}

fMRIPrep's boundary-based call on two runs of the data panel: the first echo of an 82-year-old's multi-echo BOLD run (ds003592) and a three-year-old's BOLD reference (ds000228, a small head and an oblique field of view). As panel cases beside the examples above, they are stored as three full-resolution slices; the crosshair moves through them.

{{ ev.example('fsl-flirt', 'panel-ds003592-older') }}

{{ ev.example('fsl-flirt', 'panel-ds000228-child') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, its verdict and the reason. Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('fsl-flirt') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default and warns, with `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) giving FSL's behaviour byte for byte ([register](repo:docs/findings/upstream-defects.md)). FLIRT ends with exit status 0 after any error past its command line (an image or matrix it cannot read, a matrix of the wrong size, an unknown `-bbrtype`): the replica exits 1 with FLIRT's message, and 0 in `reproduce` mode (FSL-68). What FSL leaves undefined (a schedule's matrix name it cannot interpret, `setoption bbrstep` below 1, a matrix file with a word that is not a number, `-pedir` without a field map) the replica refuses in both modes, with the reason (FSL-70 to FSL-73). FLIRT shares with mcflirt the integer outputs' clamping (FSL-09) and the treatment of infinite voxels (FSL-14).

## Known limits {#limits}

The replica is experimental. The record's standard tier holds fMRIPrep's calls on three oracle runs; its full tier (fMRIPrep's 22 calls on every oracle run with BOLD runs) and the data panel's other images run in the final validation phase. `-anglerep quaternion`, `alignpaxes`, parameter subsets other than FLIRT's own and the shipped schedules', and `-debug`'s boundary-based volume are refused with a message until they are translated. FLIRT's other programs (avscale, img2imgcoord, img2stdcoord, std2imgcoord, applyxfm4D, rmsdiff, midtrans, makerot, pointflirt) follow, and then the clean-room original. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). There is no benchmark report yet: speed is measured with the clean-room original.
