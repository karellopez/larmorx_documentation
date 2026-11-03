---
title: topup and applytopup
kicker: Tools · FSL
lede: >-
  FSL's susceptibility-distortion correction: topup estimates the off-resonance field that
  displaces echo-planar images along their phase encoding, from images acquired with opposite
  phase encodings, and applytopup corrects images with it; topup is the field-map estimation
  fMRIPrep runs for every reversed-phase-encoding (PEPOLAR) field map. An exact replica of FSL
  6.0.7.23's source in the separate larmorx-nc package (the FSL Licence's non-commercial terms),
  experimental, which gives every file both programs write, their messages and their exit status
  bit for bit in every compared case of its record, fMRIPrep's own calls included. The clean-room
  original is still to be written.
description: LARMORX's FSL topup and applytopup, exact replicas validated against FSL 6.0.7.23 — fMRIPrep's field-map estimation on two real reversed-phase-encoding pairs with every file topup writes and fMRIPrep's own outputs, FSL's own thread band beside the replica, a correction by default inside topup, applytopup's least-squares restoration, Jacobian modulation and vb3D, random testing's trial, and every parity case of the record with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-nc</code>, under the FSL Licence's terms, run as a separate program), translated from FSL 6.0.7.23's source (fsl-topup 2203.5, with fsl-basisfield, fsl-warpfns and fsl-miscmaths' optimisers and sparse matrices); clean-room original (<code>larmorx</code>, Apache-2.0): planned, to be written from <a href="{{ repo('specs/topup.md') }}">specs/topup.md</a></dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span> (replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/fsl-topup-replica.md') }}">fsl-topup-replica</a> (standard tier, FSL 6.0.7.23) · API <a href="{{ repo('docs/api/fsl-topup.md') }}">fsl-topup</a></dd>
</dl>

## What it is

An echo-planar image is displaced along its phase-encoding axis wherever the magnetic field departs from its nominal value: by the off-resonance (in Hz) times the read-out time, in voxels, and its intensity is compressed or stretched by the displacement's Jacobian. Two images with opposite phase encodings are displaced in opposite directions, so the field that makes them agree can be estimated. topup models the field as a cubic (or quadratic) B-spline, resamples each image through the displacement the field gives it (and, with `--estmov`, through its own rigid-body movement), multiplies by the Jacobian, and minimises the squared differences between the corrected images plus a regularisation of the field's bending energy (or membrane energy) weighted by `--lambda`, level by level: each level with its knot spacing (`--warpres`), subsampling, smoothing and number of iterations, by Levenberg-Marquardt or scaled conjugate gradients. It writes the field's coefficients and the movements (`--out`), and on request the corrected images (`--iout`), the field in Hz (`--fout`), each image's displacement field (`--dfout`), rigid-body matrix (`--rbmout`) and Jacobian (`--jacout`), and a log. applytopup corrects other images with topup's result: by Jacobian modulation of each image alone (`--method=jac`), by the least-squares restoration of pairs with opposite phase encodings into one image (`lsr`, the default), or by one of three undocumented variational Bayes restorations (`vb2D`, `vb3D`, `vb4D`).

fMRIPrep calls topup for every reversed-phase-encoding field map, in sdcflows' PEPOLAR workflow (`fmap_preproc_wf/<estimator>/topup`), on the average of each phase encoding's images merged into one series, with sdcflows' configuration `b02b0.cnf` (seven levels from 14 mm to 4 mm knots, without movements): `topup --config=b02b0.cnf --datain=<encoding file> --imain=<merged pair> --out --iout --fout --jacout=jac --logout --rbmout=xfm --dfout=warpfield`. sdcflows turns the coefficients into the field map fMRIPrep uses; fMRIPrep does not call applytopup, its own resampler applies the field.

```bash
larmorx fsl topup --imain=b0_pair --datain=acqparams.txt --config=b02b0.cnf --out=tu --fout=field --iout=corrected
larmorx fsl applytopup --imain=dwi_up,dwi_dn --inindex=1,2 --datain=acqparams.txt --topup=tu --out=hifi
```

```python
import larmorx as lx

acq = [[0, 1, 0, 0.0138], [0, -1, 0, 0.0138]]   # phase-encoding vector and read-out time (s)
r = lx.fsl.topup("b0_pair.nii.gz", acq, config="b02b0.cnf", fsldir="/opt/fsl", corrected=True)
field_hz = r.field                     # lx.Image on the input's grid
hifi = lx.fsl.applytopup(["dwi_up.nii.gz", "dwi_dn.nii.gz"], acq, [1, 2], r).corrected
```

FSL is distributed under the FSL Licence, which allows non-commercial use only, so LARMORX keeps its FSL tools in two implementations: the exact replica translated from FSL's source, in the separate package `larmorx-nc` (`pip install larmorx-nc`), and a clean-room original in LARMORX itself, written from a behavioural specification without FSL's code. For topup and applytopup only the replica exists so far: `implementation="auto"` (and `larmorx fsl topup`) runs it when `larmorx-nc` is installed, and a clear error names the package otherwise. The replica follows FSL 6.0.7.23, runs none of FSL's programs and needs no FSL installation (FSL's configurations by name need its `etc/flirtsch` folder, or `fsldir`); the FSL libraries topup needs (the B-spline fields with their bending- and membrane-energy regularisers, the sparse matrices, the non-linear optimisers, the warps, the spline interpolation with its derivatives, LAPACK's and OpenBLAS's arithmetic as FSL's build calls it) are translated once into `larmorx-nc`'s shared core, beside those of mcflirt, BET, FLIRT and FAST. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes: every file topup and applytopup write (each image's header and data, the coefficients, the movements, the matrices, the log), their standard output and error, and their exit status.

{{ ev.agreement('fsl-topup', 'replica') }}

The record runs 173 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-topup-replica.md)): 104 give FSL's files byte for byte, in 66 FSL refuses the input or stops and the replica does the same, with the same message and exit status (*rejected by both*), and 3 are refused by the replica in both modes where FSL needs more memory than any machine holds (a negative `--warpres`, FSL-124) or reads a field on another grid past its lines (FSL-134) (*expected divergence*). They cover fMRIPrep's call on its two oracle runs (fMRIPrep's own outputs the same too), every option of topup (double and single precision, spline and linear interpolation, both regularisers, quadratic and cubic splines, the scaling, the regridding, the minimisers per level, the movements, FSL's shipped configurations and configurations of their own, `--acqp`, x, y and oblique phase encodings, three and four volumes, `--debug`, `--trace`, `--profile`), its thread counts, every option and method of applytopup (lines of 30, 32 and 96 voxels; every data type), and every message, exit status and failure case of both command lines. Each case also runs the replica's default mode, where LARMORX corrects FSL's deterministic defects and names them (below).

## In fMRIPrep: the field map from a reversed-phase-encoding pair {#example}

fMRIPrep's own call on ds005040's pair, given to FSL 6.0.7.23 at one thread (as fMRIPrep runs it) and at four, and to the replica in its reproduce and default modes and at four threads. The two input panels are the pair before the correction; choose an output above the panels to see each image corrected, the field, the Jacobians and the displacements. The replica's differences from FSL are zero in every one; FSL's own result at four threads differs from its result at one (FSL-116): that comparison, *FSL, --nthr=4 − --nthr=1*, is the yardstick of how much FSL itself moves, and the replica gives FSL's one-thread result at any thread count. Below the viewer, every file topup writes, with fMRIPrep's own outputs (topup in fMRIPrep's image).

{{ ev.example('fsl-topup', 'fmriprep-ds005040') }}

## A second run: ds001600 {#ds001600}

fMRIPrep's call on the data panel's ds001600, a Siemens Prisma pair whose two phase encodings have different read-out times and were acquired on different grids (sdcflows resampled one onto the other first). The same runs and comparisons as above; the viewer opens on the field.

{{ ev.example('fsl-topup', 'fmriprep-ds001600') }}

## Membrane energy, and a correction by default {#membrane}

With `--regmod=membrane_energy` and Levenberg-Marquardt (the record's case `opt/membrane-lm`, on the half-resolution pair), FSL takes the regulariser's Hessian in other units than its cost and gradient: each first derivative divided by the voxel size in millimetres, where the cost counts in voxels. The replica's default takes the Hessian in the cost's units (FSL-117), so its steps follow the cost they minimise; its reproduce mode gives FSL's bytes. The difference *replica, default − reproduce mode* shows what the correction changes in the field.

{{ ev.example('fsl-topup', 'membrane') }}

## applytopup: least-squares restoration {#lsr}

applytopup's default method (the record's case `at/lsr-y`): the two images of opposite phase encodings restored into one, line by line along the phase encoding, with the field and movements of FSL's topup on the same pair. FSL resamples the first image with trilinear interpolation whatever `--interp` asks (FSL-132); the replica's default uses the method asked for, spline by default, and its reproduce mode gives FSL's bytes.

{{ ev.example('fsl-topup', 'lsr') }}

## applytopup: Jacobian modulation {#jac}

`--method=jac` (the record's case `at/jac-y`): one image corrected by itself, resampled along the phase encoding and multiplied by the displacement's Jacobian. FSL-132 reaches it too.

{{ ev.example('fsl-topup', 'jac') }}

## applytopup --method=vb3D, and a correction by default {#vb3d}

One of applytopup's undocumented variational Bayes restorations (the record's case `at/vb3d-y`): a smoothness prior within and between slices whose weights are estimated over 20 iterations. FSL builds the prior's coupling between slices with half its weight, so the precision it assembles is not positive definite and its iterations diverge: FSL's output spans about ±4 × 10<sup>10</sup> for an input of at most 1.1 × 10<sup>5</sup>, and the replica's reproduce mode gives the same bytes. The replica's default gives the prior its full weight (FSL-143), and its restoration stays in the input's range, as vb2D's does. FSL's panel is shown in the default's window; choose *each image's own* window to read it.

{{ ev.example('fsl-topup', 'vb3d') }}

## Random testing {#random}

Differential random testing's trial of this part: half an hour of random calls, each run by FSL 6.0.7.23 (through the oracle cache) and by the replica, every file compared. Every case agreed bit for bit; the record's refusals, failures and thread counts are left to the record.

{{ ev.table('fsl-topup', 'trial') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, its verdict and the reason. Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('fsl-topup') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default and warns, with `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) giving FSL's behaviour byte for byte where FSL's is defined ([register](repo:docs/findings/upstream-defects.md)). In topup: above one thread (`--nthr`, or `FSL_NUM_THREADS` for some of its matrices), FSL's result changes with the thread count; the replica gives FSL's one-thread result at any count (FSL-116, never reproduced). The membrane energy's Hessian in the cost's units (FSL-117, above). With `--regrid=1` and subsamplings whose largest does not divide the others, FSL stops at the first level with the smaller one; the replica's grid grows by their least common multiple (FSL-118). The field maps `--fout` and `--featout` write keep the input's intent parameters in place (FSL-119: FSL shifts them by one). A row-count mismatch of `--acqp` names the `--acqp` file (FSL-120). With `FSLDIR` unset and a configuration name not found, a clear error instead of FSL's exception (FSL-121). A configuration line longer than 1023 characters after its first word no longer ends the reading silently (FSL-122). A negative `--miter`, `--fwhm` or `--lambda`, which FSL uses as given, is refused (FSL-123, FSL-125, FSL-126); a negative `--warpres` is refused in both modes (FSL-124: FSL's knot spacing wraps and it exhausts the memory). In applytopup: every volume resampled with the interpolation asked for (FSL-132, above); the least-squares restoration wraps a negative index around its line (FSL-133: FSL wraps it by 2^32 modulo the line's length, wrong for lengths that do not divide 2^32, such as 30 or 96); `--method=jac` with a field image scales the displacement along y by the y voxel size (FSL-134: FSL takes the x one), and a field on another grid is refused (in both modes where FSL reads past its lines); an unknown `--method`, which FSL ignores silently (exit status 0, no output), and `lsr` or `vb*` without movements, where FSL aborts, are refused with a reason (FSL-135); the variational methods' counts of values in 64-bit integers (FSL-141: FSL's 32-bit ones wrap on very large images); vb3D and vb4D count the data points of every image (FSL-142) and build their prior with its full weight (FSL-143, above). Five defects of FSL's libraries that topup and applytopup never reach are in the register too (FSL-127 to FSL-131).

## Known limits {#limits}

The replica is experimental. The record's standard tier holds fMRIPrep's calls on its two oracle runs; its full tier, the data panel's other PEPOLAR runs and long random testing run in the final validation phase. applytopup's restorations of lines of fewer than 8 or more than 256 voxels along the phase encoding, and band systems that need LAPACK's blocked band factorisation, are refused in both modes with a message: FSL's arithmetic there follows other paths of OpenBLAS and Armadillo, which the replica does not reproduce yet. FSL's results above one thread are not reproduced (they depend on the thread count: FSL-116). The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). There is no benchmark report yet: speed is measured with the clean-room original.
