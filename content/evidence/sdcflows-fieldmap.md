---
title: sdcflows' field-map estimation
kicker: Evidence · sdcflows
lede: >-
  sdcflows turns a gradient-echo field map into the smooth field that corrects susceptibility
  distortion: the phase difference to radians and, after PRELUDE, to Hz; the field map's cubic
  B-spline fit (scikit-learn's ridge regression); the field evaluated on other grids and a series
  unwarped with it. fMRIPrep runs these steps for every phase-difference field map. LARMORX's port
  is a replica of sdcflows 2.17.1 with the arithmetic of scikit-learn, SciPy, numpy and nibabel.
  In `reproduce` it gives sdcflows' outputs bit for bit in all 37 cases of its record. On
  fMRIPrep's seven phase-difference estimators it gives them in `fix` too, and fMRIPrep's own
  files, at any thread count. Its default, `fix`, corrects sdcflows' defects or refuses them with
  a clear error, each with sdcflows' result on request. The fit takes 6.5 to 7.8 times less time
  at 14 threads, and 22 to 32 % of sdcflows' peak memory at one.
description: >-
  How LARMORX's replica of sdcflows' field-map estimation (the B-spline fit, the field evaluated
  and applied, the phase-difference preparation) compares with sdcflows 2.17.1 and its arithmetic
  of scikit-learn, SciPy, numpy and nibabel: fMRIPrep's seven phase-difference estimators on four
  fMRIPrep runs with fMRIPrep's own files, the coefficients, the unwarping of a real series, two
  corrections by default on real data (SDC-02, SDC-10), the step between two library releases,
  random testing, every case of the record with its verdict, speed and memory.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crate <code>larmorx-sdcflows</code>, <code>lx.sdcflows</code>, translated from sdcflows 2.17.1's Python (Apache-2.0): <code>BSplineApprox</code>, <code>B0FieldTransform</code>, <code>ApplyCoeffsField</code>, <code>TOPUPCoeffReorient</code>, the phase-difference workflow and its steps, with scikit-learn 1.9.1's ridge regression and the arithmetic of SciPy 1.18.1, numpy 2.5.4 (OpenBLAS 0.3.34) and nibabel 5.4.2</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span> (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/sdcflows-fieldmap.md') }}">standard comparison</a> (sdcflows 2.17.1) · benchmark <a href="{{ repo('docs/benchmarks/sdcflows-fieldmap.md') }}">sdcflows-fieldmap</a> · findings <a href="{{ repo('docs/findings/sdcflows-fieldmap.md') }}">sdcflows-fieldmap</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/sdcflows-fieldmap.md') }}">sdcflows-fieldmap</a></dd>
</dl>

## What is compared {#what-it-is}

Echo-planar images are distorted wherever the main field B₀ is not uniform: a voxel's signal is displaced along the phase-encoding axis by the local off-resonance frequency (in Hz) times the readout time. A field map measures that frequency. A gradient-echo field map stores it as a phase: the phase difference between two echoes is 2π times the frequency times the echo-time difference, known only up to whole cycles of 2π. sdcflows (the NiPreps developers, Apache-2.0) is the library fMRIPrep uses to estimate the field and correct the distortion.

For a phase-difference field map fMRIPrep 25.2.6 runs sdcflows' `init_phdiff_wf`:

- the scanner's phase map is rescaled to radians from its minimum and maximum (`au2rads`; two phase images are each rescaled and subtracted, `subtract_phases`);
- FSL's PRELUDE unwraps it inside the magnitude's brain mask;
- it is divided by 2π and the echo-time difference (`phdiff2fmap`): the field map in Hz.

sdcflows' `BSplineApprox` (fMRIPrep's node `bs_filter`) then approximates the field map by a smooth field. Its cubic B-splines sit on a control grid 16 × 16 × 10 mm apart, their coefficients fitted inside the brain mask by scikit-learn's ridge regression (`Ridge`, α = 10⁻⁴, its sparse conjugate-gradient solver). The field map's median inside the mask is subtracted before the fit, so the fitted field is centred on zero. The fitted field is evaluated everywhere (extrapolated beyond the mask), and the fitting error kept. fMRIPrep stores the coefficients and evaluates them on every grid it resamples a series onto (`B0FieldTransform`): it unwarps inside its one-shot resampler ([its page](/tools/resample-series/)), while sdcflows' own `ApplyCoeffsField` evaluates the field on the series' grid and unwarps it there.

The replica runs beside sdcflows 2.17.1, run in-process with the newest releases of the libraries under it (LARMORX's reference) and with the releases the other comparisons share. fMRIPrep's own files are the ones it wrote in its runs, with sdcflows 2.15.1 in fMRIPrep 25.2.6's image.

```python
import larmorx as lx

# fMRIPrep's phase-difference estimator: radians, PRELUDE, Hz
prep = lx.sdcflows.phdiff_workflow(
    "sub-01_magnitude1_brain.nii.gz", ["sub-01_phasediff.nii.gz"],
    [{"EchoTime1": 0.00492, "EchoTime2": 0.00738}], "sub-01_magnitude1_brain_mask.nii.gz",
    out_dir="work",
)
# the B-spline fit (fMRIPrep's bs_filter): coefficients, field, error, extrapolated field
fit = lx.sdcflows.bspline_approx(prep.fieldmap.image, "sub-01_brain_mask.nii.gz",
                                 out_dir="work", n_threads=8)
# the field on a BOLD reference, and a series unwarped with it
xf = lx.sdcflows.B0FieldTransform(coeffs=list(fit.coefficients))
xf.fit("sub-01_boldref.nii.gz")
corrected = xf.apply("sub-01_bold.nii.gz", pe_dir="j-", ro_time=0.0425, n_threads=8)
```

The [API page](repo:docs/api/sdcflows-fieldmap.md) describes every function and option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its port {#ports}

sdcflows comes under the Apache-2.0 licence, as LARMORX does, so the replica is in `larmorx` itself, translated bit for bit as ANTs and fMRIPrep's resampler are. sdcflows' Python is the specification, with the arithmetic of the libraries it calls:

- the B-spline weights stored as SciPy's sparse products store them, explicit zeros included;
- the ridge regression as scikit-learn's `sparse_cg` calls SciPy's conjugate gradients, every float32 dot product summed in the order of the OpenBLAS kernel numpy calls;
- files read and written with nibabel's arithmetic: the scale factors nibabel computes in x87's extended precision (computed exactly in LARMORX, so every platform writes Linux's bits) and the quaternions it derives with numpy's SVD and eigenvalue routines (replicated).

The heavy parts run in Rust (`larmorx-sdcflows`) on the call's threads, every sum kept in sdcflows' order, so `n_threads` never changes a bit. At one thread the fit stores its collocation matrix once (8 bytes per weight, where sdcflows and scikit-learn hold it at least three times) and reads it at every product. At more threads it evaluates the weights at every product, which is faster there and holds no matrix. The sums are the same, in the same order, either way.

PRELUDE runs through `lx.fsl.prelude` ([its page](/evidence/fsl-prelude/)). A clean room of sdcflows' steps is planned after FreeSurfer ([roadmap](/roadmap/)).

## The verdicts at a glance {#verdicts}

The replica is a translation of sdcflows' source, so the question is whether it gives sdcflows' bytes.

{{ ev.agreement('sdcflows-fieldmap', 'port') }}

The [record](repo:docs/validation/sdcflows-fieldmap.md) runs sdcflows 2.17.1 in-process as the reference, with the newest releases of the libraries under it (numpy 2.5.4 with OpenBLAS 0.3.34, SciPy 1.18.1, scikit-learn 1.9.1, nibabel 5.4.2). It compares the replica with it in `reproduce` (`upstream_defects="reproduce"`): every array, file (decompressed), header, warning and message, bit for bit. Its 37 cases pass, with 821 checks:

- **9 scripts** cover every function of the port. They run on generated inputs (odd and oblique grids, qform-only and NIfTI-2 headers, NaN values, single slices, 4D images, every option and failure) and on fMRIPrep's real calls (its phase-difference steps, its seven fits and its coefficients' reorientation), where fMRIPrep's own files of its runs are compared too.
- **28 permanent cases** come from random testing.

In 33 of the 37 the replica's default, `fix`, gives the same bytes. In the other 4 it corrects one of sdcflows' defects (SDC-01, SDC-02, SDC-07, SDC-10: *deliberate correction*, [below](#corrections)), and the record holds it to sdcflows' own construction with the correction made in its pieces.

## In fMRIPrep: seven phase-difference estimators {#fmriprep}

fMRIPrep 25.2.6 estimated seven phase-difference field maps on four of its runs: ds005454-sub-16 (7 T), ds002603-sub-01, ds002422-sub-02 (two, at 1.5 T) and ds001600-sub-1 (three protocols). Each estimator's nodes were run again here on the inputs fMRIPrep gave them:

- sdcflows 2.17.1 with the newest releases and with the releases the other comparisons share;
- the replica at 1 and 14 threads, in `fix` and in `reproduce`;
- the replica's whole workflow with PRELUDE's clean room (`lx.fsl.prelude`).

fMRIPrep's own files stand beside them. Every comparison gives the same values, every one.

In each example below the input panels are the scanner's phase map, the magnitude, sdcflows' brain mask over it and fMRIPrep's unwrapped phase (PRELUDE's output, which the next step turns into Hz). The outputs, chosen above the viewer, are the phase difference in radians, the field map in Hz, the fitted field extrapolated over the field of view, and the fitting error inside the mask. The viewer opens on the field map.

### ds005454: a GRE phase difference at 7 T {#ds005454}

{{ ev.example('sdcflows-fieldmap', 'estimator-ds005454') }}

### ds002603: a Philips phase difference at 2 mm {#ds002603}

{{ ev.example('sdcflows-fieldmap', 'estimator-ds002603') }}

### ds002422: a phase difference at 1.5 T {#ds002422}

The data panel's 1.5 T subject has two phase-difference maps on different grids; the first is shown, both are in the table below.

{{ ev.example('sdcflows-fieldmap', 'estimator-ds002422-run01') }}

### Every estimator {#estimators}

{{ ev.table('sdcflows-fieldmap', 'estimators') }}

## The coefficients {#coefficients}

What fMRIPrep keeps of the fit is one coefficient per control point (4,352 on ds005454's grid). The replica's coefficients are sdcflows' and fMRIPrep's own file, every one: scikit-learn's conjugate gradients (354 iterations here), each float32 sum taken in OpenBLAS's order.

{{ ev.example('sdcflows-fieldmap', 'coefficients-ds005454') }}

## The unwarping of a real series, and SDC-02 {#apply}

sdcflows' `ApplyCoeffsField` ran on the first 10 volumes of ds005454's resting-state series, with fMRIPrep's coefficients and fMRIPrep's registration of the BOLD reference to the field map. The replica's unwarped series is sdcflows', every value, at 1 and 14 threads.

The registration rotates the series' grid against the coefficients' grid, and there sdcflows' weights are wrong. It multiplies, per axis, weights each taken from one index of the voxel, a product that is exact only for aligned grids (SDC-02). The replica's default, `fix`, evaluates the B-splines at each voxel's position and names SDC-02; in `reproduce` it gives sdcflows' series. On this call the field changes by 3.65 Hz RMS inside the brain (31.3 Hz at most), and the series by 8.73 RMS over all its values, in the image's units (its range is 2,417): compare *fix − reproduce*.

{{ ev.example('sdcflows-fieldmap', 'apply-ds005454') }}

## SDC-10: the field on an oblique BOLD reference {#sdc10}

When the target of `B0FieldTransform.fit` is not aligned with the coefficients' grid, sdcflows evaluates the field on a fine aligned grid around the target and interpolates it onto the target with cubic B-splines. It builds that grid around the target as given and samples it at the target's own coordinates, so the registration to the field map (`xfm_data2fmap`) is ignored: the field is taken where the target lies before it is registered (SDC-10). fMRIPrep's own reconstruction never takes this path (it refuses grids that are not aligned); sdcflows' unwarping does.

On ds002603's two oblique BOLD references, with fMRIPrep's registration, sdcflows' field departs from the known answer, the exact field, by 8.48 and 7.67 Hz RMS inside the brain (up to 87 Hz). The replica's default, `fix`, builds and samples the grid where the transform puts the target and gives the exact field within 10⁻⁴ Hz (its float32 sums of the B-splines in another order). In `reproduce` it gives sdcflows' field.

{{ ev.example('sdcflows-fieldmap', 'sdc10-ds002603') }}

{{ ev.table('sdcflows-fieldmap', 'sdc10') }}

## SDC-06: fMRIPrep's own field maps fitted again {#sdc06}

fMRIPrep writes its field maps as 4D images of one volume. Given one of them, sdcflows' `BSplineApprox` stops with a `ValueError` (the header's four voxel sizes broadcast against three). The replica's default, `fix`, fits the map as the 3D image it is (SDC-06); in `reproduce` it raises sdcflows' error.

{{ ev.table('sdcflows-fieldmap', 'sdc06') }}

## Corrections by default {#corrections}

Every defect the replica found in sdcflows was decided by the register's rules (A: corrected by default; B: refused with a clear error; C: kept and documented; D: measured first). `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) gives sdcflows' behaviour, its errors and warnings included ([findings](repo:docs/findings/sdcflows-fieldmap.md), [register](repo:docs/findings/upstream-defects.md)). Eight are corrected by default and two refused with a reason. SDC-03, in `CheckRegister`'s branch for two magnitude images, needs FreeSurfer's `mri_robust_register` and comes with FreeSurfer's port. fMRIPrep's calls meet none of them; sdcflows' own interfaces and workflows do (SDC-02 and SDC-10 above, on real data).

{{ ev.table('sdcflows-fieldmap', 'corrections') }}

## The originals' own step: two library releases {#step}

Each case also runs sdcflows with the releases the other comparisons share (numpy 2.3.5 with OpenBLAS 0.3.30, SciPy 1.15.3) and says what changed from them to the newest, line by line. sdcflows' code on these paths is the same in 2.15.1 (fMRIPrep 25.2.6's) and 2.17.1, scikit-learn's solver is the same from 1.6.1 to 1.9.1, and SciPy's routines on these paths do the same arithmetic from 1.15 to 1.18.

Of 381 compared lines 4 change, all for one reason: numpy's OpenBLAS 0.3.31 and later bundle LAPACK 3.12.1, which moves the last bits of numpy's SVD and eigenvalue routines. So nibabel writes other NIfTI quaternions for some oblique affines, and decides a rotation with two equal candidate axes otherwise. The replica follows LAPACK 3.12.1 and reproduces 3.12.0 for the comparison in the shared environment.

{{ ev.table('sdcflows-fieldmap', 'step') }}

## Speed {#speed}

The benchmark ([report](repo:docs/benchmarks/sdcflows-fieldmap.md)) runs sdcflows' interfaces in-process and the replica on fMRIPrep's seven `bs_filter` calls and on `ApplyCoeffsField` with 60 volumes of ds005454. It times the whole interface (reading, the fit or the unwarping, writing every file) and checks every output byte for byte. sdcflows' fit has no thread option: scikit-learn's conjugate gradients run on one thread.

- The replica at 14 threads takes 6.5 to 7.8 times less time (ds002603's 128³ field map with 9,072 coefficients: 4.0 s against 27.5 s).
- At one thread, in a fresh process, it takes 1.09 to 1.14 times less.
- `ApplyCoeffsField` takes 1.7 times less time at 1 and at 14 threads.

The machine was shared with other work.

{{ ev.speed('sdcflows-fieldmap') }}

## Memory {#memory}

The memory rule allows LARMORX at most 10 % above the original's peak plus 8 MiB for the same call; here the replica needs 22 to 32 % of sdcflows' peak.

{{ ev.table('sdcflows-fieldmap', 'memory') }}

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through sdcflows and the replica and compares every output ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a permanent case, registered as a defect of sdcflows, or reported. The replica's random-testing run of 2026-11-08 lasted half an hour:

{{ ev.table('sdcflows-fieldmap', 'trial') }}

{{ ev.table('sdcflows-fieldmap', 'triage') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('sdcflows-fieldmap') }}

## Known limits {#limits}

- This page covers the field-map model and the phase-difference preparation. PEPOLAR's and SyN's steps, sdcflows' masks, niworkflows' helpers, fMRIPrep's own field-map steps and sdcflows' command line are on [their own page](/evidence/sdcflows-estimation/).
- `CheckRegister`'s branch for two magnitude images waits for FreeSurfer's `mri_robust_register` (SDC-03).
- At one thread the stored collocation matrix's speed depends on what the process ran before. In the benchmark, ds001600's one-thread fits took 0.86 times sdcflows' time after its first calls in the same process, and 1.1 times less in a fresh one ([the report](repo:docs/benchmarks/sdcflows-fieldmap.md), footnote 1). To be measured before larmorprepx runs fits in a long-lived process.
- The record's standard comparison holds fMRIPrep's calls on its runs; the full comparisons and long random testing run in the final validation phase.
- The other five platforms are held to LARMORX's own Linux output by the [cross-platform checks](repo:docs/validation/golden.md).

## History {#history}

- **2026-11-08**: the replica, translated from sdcflows 2.17.1 with scikit-learn's, SciPy's, numpy's and nibabel's arithmetic; sdcflows' defects SDC-01 to SDC-11 found, each corrected by default, refused with a clear error or waiting for FreeSurfer's port; its record and its random-testing run ([the roadmap](/roadmap/)).
- **2026-11-10**: PEPOLAR, direct and fieldmap-less estimation, sdcflows' masks and BIDS app, on [their own page](/evidence/sdcflows-estimation/).
