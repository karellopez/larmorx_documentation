---
title: t2smap
kicker: Tools · tedana
lede: >-
  tedana's T2* and S0 maps of multi-echo fMRI and the echoes' optimal combination: the step
  fMRIPrep runs for every multi-echo BOLD run, whose combined series it carries on with. An exact
  replica of tedana 26.0.3's source in the separate larmorx-gpl package (the GNU GPL version 3,
  converted from tedana's LGPL-2.1), experimental, with the arithmetic of numpy, SciPy, nibabel
  and nilearn: every file t2smap writes, its messages and its exit status bit for bit in every
  compared case of its record, in both kept library environments, fMRIPrep's five calls on three
  oracle runs included, at any thread count. tedana's defects found by the replica are corrected
  by default or refused with a clear error, each with tedana's result on request. On fMRIPrep's
  calls it needs 44 % of tedana's peak memory and, at 14 threads, a quarter to a third of its time. The
  clean-room original, the fast one, comes later in the main package.
description: LARMORX's tedana t2smap, an exact replica validated against tedana 26.0.3 with numpy, SciPy, nibabel and nilearn in two library environments — fMRIPrep's multi-echo calls on three oracle runs with fMRIPrep's own files (tedana 25.0.1), the T2* and S0 maps and the optimally combined series of a real run, tedana's own variability (numpy's AVX-512 kernels, library releases, threads, versions), the defects TED-01 to TED-18 with the corrections by default, random testing, every parity case with its verdict, memory and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>exact replica (<code>larmorx-gpl</code>, the GNU GPL version 3 only, run as a separate program: crates <code>larmorx-gpl-tedana</code> and <code>larmorx-gpl-cli</code>), translated from tedana 26.0.3's source with the arithmetic of numpy 2.5.4 (OpenBLAS 0.3.34), SciPy 1.18.1, nibabel 5.4.2 and nilearn 0.14.1, whose permissive pieces live in <code>larmorx</code> itself; the clean-room original (<code>larmorx</code>, Apache-2.0) is still to be written, from <a href="{{ repo('specs/t2smap.md') }}">specs/t2smap.md</a></dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span> (replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/tedana-t2smap-replica.md') }}">tedana-t2smap-replica</a> (standard tier, tedana 26.0.3) · findings <a href="{{ repo('docs/findings/tedana-t2smap.md') }}">tedana-t2smap</a> · benchmark <a href="{{ repo('docs/benchmarks/tedana-t2smap.md') }}">tedana-t2smap</a> · API <a href="{{ repo('docs/api/tedana-t2smap.md') }}">tedana-t2smap</a></dd>
</dl>

## What it is

A multi-echo BOLD run records every volume at several echo times. In each voxel the signal decays with the echo time TE as S(TE) = S0 · exp(−TE / T2*): S0 is the signal at TE = 0 and T2* the decay's time constant, which the BOLD effect changes. tedana (*TE-Dependent ANAlysis*, the ME-ICA developers; DuPre et al., 2021, JOSS 6:3669) estimates both in every voxel and combines the echoes into one series that keeps the BOLD contrast of every echo. Its `t2smap` workflow first counts, in each voxel of the mask, the echoes whose signal is good (the *adaptive mask*: an echo whose mean signal drops below a third of that of the voxels the 33rd percentile marks is not); it then fits the decay through those echoes, at least two: log-linearly (a least-squares line through log(|S| + 1) against TE, for each count of echoes all voxels at once) or, with `--fittype curvefit`, by a monoexponential least-squares fit started from the log-linear one, its S0 bounded below by the voxel's lowest signal; it floors and caps the maps (the *limited* maps leave out the voxels with one good echo), measures the fit's error per voxel and per volume, and weighs every echo by TE · exp(−TE / T2*) with the voxel's T2* (Posse et al., 1999), or by its temporal signal-to-noise ratio (`--combmode paid`; Poser et al., 2006).

fMRIPrep 25.2.6 runs it for every multi-echo BOLD run (`init_bold_t2s_wf`, its `T2SMap` interface): `t2smap -d <the echoes, resampled onto the BOLD reference> -e <the echo times in ms> --mask <the BOLD mask dilated by two voxels> --fittype curvefit` (`--me-t2s-fit-method`, curvefit by default), with one thread, and keeps the full T2* map and the optimally combined series.

```bash
larmorx tedana t2smap -d echo-1.nii.gz echo-2.nii.gz echo-3.nii.gz -e 14.0 29.96 45.92 \
    --mask mask.nii.gz --fittype curvefit --out-dir t2smap
```

```python
import larmorx as lx

res = lx.tedana.t2smap(["echo-1.nii.gz", "echo-2.nii.gz", "echo-3.nii.gz"],
                       [0.014, 0.02996, 0.04592], mask="mask.nii.gz", fittype="curvefit")
res.t2star, res.s0, res.optcom, res.adaptive_mask, res.fit_failures, res.confounds
```

tedana is licensed under the GNU LGPL version 2.1, so its replica lives in its own package, `larmorx-gpl` (`pip install larmorx-gpl`, or `pip install "larmorx[all]"`), under the GNU GPL version 3, which the LGPL's section 3 allows ([licensing](repo:docs/licensing.md)); `lx.tedana.t2smap` and `larmorx tedana t2smap` run its program when it is installed, and say how to install it otherwise. The arithmetic it relies on is permissive and lives in LARMORX itself: numpy's least squares (LAPACK 3.12's `dgelsd` over each group of voxels at once, with OpenBLAS's Haswell kernels), SciPy's bounded trust-region fit (`least_squares`' TRF method, its finite-difference Jacobian and its SVD), numpy's float32 log (numpy's own kernel), its sums, means and percentiles, glibc 2.35's float64 exp and log (what numpy calls on CPUs without AVX-512), nilearn's mask when none is given, and nibabel's and nilearn's writers (the quaternion in x87's extended precision included). The replica divides the voxels between threads in fixed pieces, so `--n-threads` never changes a bit. In its default mode it names the maths entries NP-03 and GLIBC-07 exactly where the correctly rounded functions change a written value, by running the stages from the mask to the combination again with the other choice of functions, writing nothing: up to four passes, so the replica is as fast as tedana at one thread; the clean-room original, written from the [specification](repo:specs/t2smap.md), will be the fast implementation. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

The replica is a translation of tedana's source, so the question for it is whether it gives tedana's bytes: every image (header and data), the confounds table, the JSON files, the messages and the exit status.

{{ ev.agreement('tedana-t2smap', 'replica') }}

The [record](repo:docs/validation/tedana-t2smap-replica.md) runs tedana 26.0.3 as its program in both kept library environments, the newest releases (numpy 2.5.4 with OpenBLAS 0.3.34, SciPy 1.18.1: LARMORX's reference) and the shared ones (numpy 2.3.5 with OpenBLAS 0.3.30, SciPy 1.15.3), numpy's OpenBLAS on its Haswell kernels, numpy's AVX-512 kernels off and one BLAS thread, and compares the replica with each in its reproduce mode (`upstream_defects="reproduce"`), with that environment's libraries. Of its 69 cases 44 pass, every file, message and exit status the same in both environments, and in 25 both programs refuse the input with the same messages and exit status; none differs. The cases cover fMRIPrep's five calls on three oracle runs (ds003592's also with `--fittype loglin`), every option (masks given and computed, every mask type, both fit types and fit modes, both combinations, dummy scans and excluded volumes, both naming conventions, prefixes, `--verbose`, runs made twice with and without `--overwrite`), every data type and file form (float32, float64, scaled int16, uint16 and uint8, big-endian, `.nii`, `.nii.gz`, pairs, NIfTI-2, z-concatenated echoes), NaN, infinite, zero and negative samples, one volume and nine echoes, every failure case, tedana's own variability, and 18 cases from random testing. Each case also runs the default mode, where LARMORX corrects tedana's deterministic defects and names them (below).

## In fMRIPrep: the T2* and S0 maps {#fmriprep}

fMRIPrep's own call on its oracle run of OpenNeuro ds003592 sub-280 (three echoes, 200 volumes), given to tedana 26.0.3, to the replica and to tedana itself in other settings: numpy's AVX-512 kernels on (this CPU's default), the shared environment's releases, four threads, and tedana 25.0.1 in fMRIPrep's image. fMRIPrep keeps the full T2* map, so its own file is compared with that map. The input panels are the first volume of each echo as fMRIPrep gives it to t2smap and fMRIPrep's mask over the first echo; the outputs, chosen above the viewer, are the full and the limited maps, the adaptive mask and the curve fit's failures. The viewer opens on the full T2* map, where the default mode's correction TED-05 is largest: tedana 26.0.x caps only the limited map (values more than ten times its 99.5th percentile are set to it), so a few voxels of the full map, the map fMRIPrep keeps and the combination uses, hold values of a hundred thousand seconds; tedana 25.0.1, fMRIPrep's, capped the full map, and LARMORX's default does.

{{ ev.example('tedana-t2smap', 'maps-ds003592') }}

### The optimally combined series {#optcom}

{{ ev.example('tedana-t2smap', 'optcom-ds003592') }}

### ds000258: four echoes, big-endian, oblique {#ds000258}

OpenNeuro ds000258 sub-21262's resting-state run: four echoes on an oblique grid stored left–posterior–superior; the raw echoes are big-endian int16, and the echoes fMRIPrep gives t2smap keep their byte order, big-endian float32.

{{ ev.example('tedana-t2smap', 'maps-ds000258') }}

### Every call {#calls}

fMRIPrep 25.2.6 ran t2smap five times on three oracle runs: ds003592's run (with its log-linear fit added by the record), ds000210 sub-02's two runs and ds000258's. In every one the replica gives tedana 26.0.3's files in both environments; fMRIPrep's own files, made by tedana 25.0.1, differ from tedana 26.0.3's for reasons the table's note lists, and from LARMORX's default about as much.

{{ ev.table('tedana-t2smap', 'calls') }}

## Every file {#files}

The two calls shown above, file by file: the replica's every value is tedana's, the RMSE map (NaN where fewer than two echoes are good) and the confounds table included, at 1 and 14 threads; its default changes what the corrections change; tedana's own runs show how much tedana varies with its kernels, releases, threads and version.

{{ ev.table('tedana-t2smap', 'files') }}

## tedana's own variability {#spread}

The record's spread cases measure how much tedana 26.0.3 varies on one machine when one setting changes: numpy's AVX-512 kernels for float64 exp and log (NP-04: Intel's SVML kernels, which numpy uses by default on this CPU; LARMORX's reference is the path without them, decision D2), the library releases (SciPy's trust-region method changed between 1.15 and 1.18), four threads (tedana's curve fits in four processes) and its version (25.0.1, in fMRIPrep's image on this machine). The replica gives the same bytes at any thread count.

{{ ev.table('tedana-t2smap', 'spread') }}

## Corrections by default {#corrections}

Every defect the replica found in tedana was decided by the register's rules (A: corrected by default; B: refused with a clear error; C: kept and documented; D: measured first), and `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) gives tedana's behaviour, its errors and messages included ([findings](repo:docs/findings/tedana-t2smap.md)). fMRIPrep's calls meet TED-05 (the full T2* map uncapped, every call), TED-08 (a failed fit of a voxel with one good echo not marked in the failures map, three of the four curve-fit calls) and the maths entries NP-03 and GLIBC-07, all corrected and named by default; the other entries need inputs or options fMRIPrep does not give.

{{ ev.table('tedana-t2smap', 'corrections') }}

## Speed {#speed}

The benchmark ([report](repo:docs/benchmarks/tedana-t2smap.md)) runs tedana 26.0.3 and the replica on fMRIPrep's five calls, the whole command timed (reading, the masks, the fits, the maps, the combination, writing), every reproduce run's files checked against tedana's. At 14 threads the replica takes 3.0 to 4.2 times less time than tedana on the curve-fit calls; at one thread about as long (0.8 to 1.1 times tedana's speed), because both modes run up to four passes to name the maths entries exactly; on the log-linear call, which tedana finishes in 6 s, those passes make it slower. The machine was shared with another agent's work.

{{ ev.speed('tedana-t2smap') }}

## Memory {#memory}

The memory rule allows LARMORX at most 10 % above the original's peak plus 8 MiB for the same call; here the replica needs 44 % of tedana's peak.

{{ ev.table('tedana-t2smap', 'memory') }}

## Random testing {#random-testing}

Random testing runs random valid and invalid multi-echo inputs and option combinations through tedana and the replica and compares every output ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of tedana, or reported. The trial of this part ran half an hour, and a check of the final build ten minutes:

{{ ev.table('tedana-t2smap', 'trial') }}

{{ ev.table('tedana-t2smap', 'triage') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('tedana-t2smap') }}

## Known limits {#limits}

The replica reads NIfTI-1 and -2 (`.nii`, `.nii.gz`, pairs), ANALYZE and MGH; the other formats nibabel reads (AFNI, MINC, PAR/REC) are refused with a clear message, a documented gap. Its log lines are tedana's; Python's warnings name the replica's own place instead of tedana's installed file, its progress bars are its own, and `dataset_description.json` describes the replica and the library releases it reproduces where tedana describes its Python (decision D6). It reproduces tedana 26.0.3, not 25.0.1, fMRIPrep 25.2.6's: the step between the two is measured above, not reproduced. The record's standard tier holds fMRIPrep's calls on its three multi-echo oracle runs; the full tiers and long random testing run in the final validation phase. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). The clean-room original, written from [specs/t2smap.md](repo:specs/t2smap.md) by an implementer who never reads tedana's source, comes later in the main package.
