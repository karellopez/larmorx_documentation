---
title: t2smap
kicker: Evidence · tedana
lede: >-
  `t2smap` is tedana's fit of the T2* and S0 maps of multi-echo fMRI and its optimal combination of
  the echoes. fMRIPrep runs it for every multi-echo BOLD run and carries on with the combined
  series. The replica (`larmorx-gpl`) gives tedana 26.0.3's files, messages and exit status bit for
  bit in all 62 of its compared cases, out of 102, in both kept library environments and at any
  thread count; fMRIPrep's four calls on three fMRIPrep runs are among them. The clean room
  (`larmorx`, from the next release) holds tedana's results within its specification's thresholds
  in 88 of its 89 compared cases, out of 125, fMRIPrep's four calls among them, the same files at
  any thread count; in the other, a chaotic curve fit, it does not print SciPy's own warnings. On
  fMRIPrep's curve-fit calls the clean room runs 10 to 15 times as fast as tedana on one thread and
  19 to 30 times on eight, with a quarter of tedana's peak memory. Both correct tedana's defects by
  default or refuse them with a clear error, each with tedana's result on request.
description: >-
  How LARMORX's two ports of tedana's t2smap, a replica and a clean room, compare with tedana
  26.0.3 and its arithmetic of numpy, SciPy, nibabel and nilearn: fMRIPrep's multi-echo calls on
  three fMRIPrep runs with fMRIPrep's own files (tedana 25.0.1, reproduced exactly here with numpy's
  kernels as in fMRIPrep's runs), the T2* and S0 maps and the optimally combined series of real
  runs by tedana and both ports, tedana's own variability, the defects with the corrections by
  default, random testing of both ports, every case of both records with its verdict, memory and
  speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx-gpl</code> <span class="port-licence">GPL-3.0</span>: crates <code>larmorx-gpl-tedana</code> and <code>larmorx-gpl-cli</code>, translated from tedana 26.0.3's source with the arithmetic of numpy 2.5.4 (OpenBLAS 0.3.34), SciPy 1.18.1, nibabel 5.4.2 and nilearn 0.14.1, whose permissive pieces live in <code>larmorx</code> itself; it runs as a separate program</li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crate <code>larmorx-tedana</code>, written from <a href="{{ repo('specs/t2smap.md') }}">specs/t2smap.md</a>, tedana's documentation, the papers it names and runs of tedana 26.0.3 and of the replica, without tedana's source (2026-11-11 and 12); from the next release</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--experimental">experimental</span>; clean room <span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/tedana-t2smap-replica.md') }}">standard comparison</a> (tedana 26.0.3) · the clean room's: <a href="{{ repo('docs/validation/tedana-t2smap-original.md') }}">full comparison</a> (tedana 26.0.3) · findings: the replica's <a href="{{ repo('docs/findings/tedana-t2smap.md') }}">tedana-t2smap</a>, the clean room's <a href="{{ repo('docs/findings/tedana-t2smap-clean-room.md') }}">tedana-t2smap-clean-room</a> · benchmark <a href="{{ repo('docs/benchmarks/tedana-t2smap.md') }}">tedana-t2smap</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/tedana-t2smap.md') }}">tedana-t2smap</a></dd>
</dl>

## What is compared {#what-it-is}

A multi-echo BOLD run records every volume at several echo times. In each voxel the signal decays with the echo time TE as S(TE) = S0 · exp(−TE / T2*): S0 is the signal at TE = 0 and T2* the decay's time constant, which the BOLD effect changes. tedana (*TE-Dependent ANAlysis*, the ME-ICA developers; DuPre et al., 2021, JOSS 6:3669) estimates both in every voxel and combines the echoes into one series that keeps the BOLD contrast of every echo.

Its `t2smap` workflow works in four steps:

- it counts, in each voxel of the mask, the echoes whose signal is good: the *adaptive mask*. An echo whose mean signal drops below a third of that of the voxels the 33rd percentile marks is not good;
- it fits the decay through those echoes, at least two. The fit is log-linear (a least-squares line through log(|S| + 1) against TE, for each count of echoes all voxels at once) or, with `--fittype curvefit`, a monoexponential least-squares fit started from the log-linear one, its S0 bounded below by the voxel's lowest signal;
- it floors and caps the maps (the *limited* maps leave out the voxels with one good echo) and measures the fit's error per voxel and per volume;
- it weighs every echo by TE · exp(−TE / T2*) with the voxel's T2* (Posse et al., 1999), or by its temporal signal-to-noise ratio (`--combmode paid`; Poser et al., 2006).

fMRIPrep 25.2.6 runs it for every multi-echo BOLD run (`init_bold_t2s_wf`, its `T2SMap` interface): `t2smap -d <the echoes, resampled onto the BOLD reference> -e <the echo times in ms> --mask <the BOLD mask dilated by two voxels> --fittype curvefit` (`--me-t2s-fit-method`, curvefit by default), with one thread. It keeps the full T2* map and the optimally combined series.

The two ports run beside tedana 26.0.3's `t2smap` on the same files with the same arguments. fMRIPrep's own files are the ones it wrote in its runs, with tedana 25.0.1 in fMRIPrep 25.2.6's image.

```bash
larmorx --implementation clean-room tedana t2smap -d echo-1.nii.gz echo-2.nii.gz echo-3.nii.gz \
    -e 14.0 29.96 45.92 --mask mask.nii.gz --fittype curvefit --out-dir t2smap
```

```python
import larmorx as lx

res = lx.tedana.t2smap(["echo-1.nii.gz", "echo-2.nii.gz", "echo-3.nii.gz"],
                       [0.014, 0.02996, 0.04592], mask="mask.nii.gz", fittype="curvefit",
                       implementation="clean-room")
res.t2star, res.s0, res.optcom, res.adaptive_mask, res.fit_failures, res.confounds
```

Both choose the clean room, which comes with the next release; in 0.1.0rc1 `t2smap` is the replica only, in `larmorx-gpl`. The [API page](repo:docs/api/tedana-t2smap.md) describes every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

tedana comes under the GNU LGPL version 2.1, so LARMORX keeps `t2smap` in two ports ([licensing](repo:docs/licensing.md)).

The replica lives in its own package, `larmorx-gpl` (`pip install larmorx-gpl`, or `pip install "larmorx[all]"`), under the GNU GPL version 3, which the LGPL's section 3 allows. It runs as its own program.

- The arithmetic it relies on is permissive and lives in LARMORX itself: numpy's least squares (LAPACK 3.12's `dgelsd` over each group of voxels at once, with OpenBLAS's Haswell kernels), SciPy's bounded trust-region fit (`least_squares`' TRF method, its finite-difference Jacobian and its SVD), numpy's float32 log (numpy's own kernel), its sums, means and percentiles, glibc 2.35's float64 exp and log (what numpy calls on CPUs without AVX-512), nilearn's mask when none is given, and nibabel's and nilearn's writers (the quaternion in x87's extended precision included).
- It divides the voxels between threads in fixed pieces, so `--n-threads` never changes a bit.
- In its default, `fix`, it names the maths entries NP-03 and GLIBC-07 exactly where the correctly rounded functions change a written value. To do so it runs the stages from the mask to the combination again with the other choice of functions, writing nothing: up to four passes, so the replica is as fast as tedana at one thread.

The clean room is part of LARMORX itself (`pip install larmorx`, Apache-2.0) and runs in the same process. Its implementers worked from the [specification](repo:specs/t2smap.md), tedana's documentation, the papers it names and runs of tedana and of the replica as black boxes, never from tedana's source or the replica's code. It is built for speed:

- the log-linear fit in closed form, voxel by voxel;
- its own trust-region curve fit on the echoes' means, where each evaluation costs as many operations as there are echoes, not echoes times volumes;
- the work divided between threads in fixed pieces, so `--n-threads` never changes a bit.

In `reproduce` it gives tedana's defects exactly and its fitted numbers within the specification's thresholds (its §17.3), not bit for bit. The exception is the voxels whose observations are all equal, where tedana's values are its least squares' rounding noise (TED-46): there it computes them with LARMORX's exact ports of numpy's `lstsq` and SciPy's `curve_fit`.

`implementation="auto" | "replica" | "clean-room"` chooses between them. `auto` (the default, and `larmorx tedana t2smap` without `--implementation`) takes the replica when `larmorx-gpl` is installed, else the clean room.

## The verdicts at a glance {#verdicts}

The replica is a translation of tedana's source, so the question for it is whether it gives tedana's bytes: every image (header and data), the confounds table, the JSON files, the messages and the exit status.

{{ ev.agreement('tedana-t2smap', 'replica') }}

The replica's [record](repo:docs/validation/tedana-t2smap-replica.md) runs tedana 26.0.3 as its program in both kept library environments, with numpy's OpenBLAS on its Haswell kernels, numpy's AVX-512 kernels off and one BLAS thread:

- the newest releases (numpy 2.5.4 with OpenBLAS 0.3.34, SciPy 1.18.1), LARMORX's reference;
- the shared ones (numpy 2.3.5 with OpenBLAS 0.3.30, SciPy 1.15.3).

It compares the replica with each in `reproduce` (`upstream_defects="reproduce"`), with that environment's libraries. Of its 102 cases:

- **Bit-identical, 62.** Every file, message and exit status the same in both environments.
- **Rejected by both, 40.** tedana refuses the input, and the replica does the same, with the same messages and exit status.

None differs. The cases cover:

- fMRIPrep's four calls on three fMRIPrep runs (ds003592's also with `--fittype loglin`; ds000210's and ds000258's from the fMRIPrep runs made with OpenBLAS's Haswell kernels);
- every option: masks given and computed, every mask type, both fit types and fit modes, both combinations, dummy scans and excluded volumes, both naming conventions, prefixes, `--verbose`, runs made twice with and without `--overwrite`;
- every data type and file form: float32, float64, scaled int16, uint16 and uint8, big-endian, `.nii`, `.nii.gz`, pairs, NIfTI-2, z-concatenated echoes, and 20 cases of ANALYZE 7.5 and MGH/MGZ;
- NaN, infinite, zero and negative samples, one volume and nine echoes;
- every failure case, with tedana's chained tracebacks;
- tedana's own variability, and 18 cases from random testing.

Each case also runs the replica's default, `fix`, where LARMORX corrects tedana's deterministic defects and names them ([below](#corrections)).

The clean room is not a translation but an implementation of the specification, so the question for it is whether it behaves as tedana does within the specification's thresholds (§17.3, by its `check.py`):

- its exit statuses, files, headers, data types, messages and the defects it names are tedana's in `reproduce` (A) and the replica's default's in `fix` (B);
- its fitted numbers are judged value by value; where a curve fit is ill-conditioned (a flat objective or a start on the feasibility boundary), by the fit's own objective, with at most 3 % of a call's fit voxels judged that way.

{{ ev.agreement('tedana-t2smap', 'original') }}

The clean room's [record](repo:docs/validation/tedana-t2smap-original.md) runs 125 cases of its full comparison against tedana 26.0.3 (through the cache of the original's runs), and each case's `fix` against the `fix` of a replica built from the same branch:

- **Bit-identical, 65.** tedana's values bit for bit.
- **Within the thresholds, 23.** tedana's values within §17.3's thresholds.
- **Rejected by both, 36.** Both programs refuse the input with the same messages and exit status.
- **Expected divergence, 1.** A chaotic curve fit, inside whose steps SciPy prints its own floating-point warnings; the clean room does not print them, since its solver is its own.

None fails. The cases cover the specification's black-box probe and more:

- every option: masks given and computed, both fit types and modes, both combinations, dummy scans and excluded volumes, both naming conventions, prefixes, `--verbose`;
- every data type and file form: NIfTI-1 and -2, pairs, z-concatenated echoes, ANALYZE 7.5, MGH/MGZ;
- NaN, infinite, zero and negative samples, and the saturated voxels of TED-46 in both fits and both modes;
- every failure case, and thread invariance at 1, 4 and 8 threads;
- fMRIPrep's four calls on three fMRIPrep runs (ds003592's also with `--fittype loglin` and with `--verbose`; ds000210's two runs and ds000258's from the fMRIPrep runs made with OpenBLAS's Haswell kernels).

## In fMRIPrep: the T2* and S0 maps {#fmriprep}

fMRIPrep's own call on its run of OpenNeuro ds003592 sub-280 (three echoes, 200 volumes) was given to tedana 26.0.3, to both ports and to tedana itself in other settings: numpy's AVX-512 kernels on (this CPU's default), the shared environment's releases, four threads, and tedana 25.0.1 in fMRIPrep's image, with numpy's AVX-512 kernels off and on. The replica ran in `reproduce` at 1 and 14 threads and in `fix`; the clean room in `reproduce` at one thread and in `fix` at eight and at one. fMRIPrep keeps the full T2* map, so its own file is compared with that map.

The input panels are the first volume of each echo as fMRIPrep gives it to t2smap, and fMRIPrep's mask over the first echo. The outputs, chosen above the viewer, are the full and the limited maps, the adaptive mask and the curve fit's failures. The viewer opens on the full T2* map, where the default's correction TED-05 is largest. tedana 26.0.x caps only the limited map (values more than ten times its 99.5th percentile are set to it), so a few voxels of the full map, the map fMRIPrep keeps and the combination uses, hold values of a hundred thousand seconds. tedana 25.0.1, fMRIPrep's, capped the full map, and LARMORX's default does.

{{ ev.example('tedana-t2smap', 'maps-ds003592') }}

### The optimally combined series {#optcom}

{{ ev.example('tedana-t2smap', 'optcom-ds003592') }}

### ds000258: four echoes, big-endian, oblique {#ds000258}

OpenNeuro ds000258 sub-21262's resting-state run has four echoes on an oblique grid stored left–posterior–superior. The raw echoes are big-endian int16, and the echoes fMRIPrep gives t2smap keep their byte order, big-endian float32. Its fMRIPrep run was made again on 2026-11-09 on this machine with OpenBLAS's Haswell kernels, and numpy's AVX-512 kernels on (the run's settings name only OpenBLAS's). tedana 25.0.1, run here in fMRIPrep's image the same way, gives fMRIPrep's own T2* map bit for bit; with numpy's AVX-512 kernels off 629 of its values differ (the two comparisons of tedana 25.0.1 with fMRIPrep's output).

{{ ev.example('tedana-t2smap', 'maps-ds000258') }}

### Every call {#calls}

fMRIPrep 25.2.6 ran t2smap four times on three fMRIPrep runs: ds003592's run, ds000210 sub-02's two runs and ds000258's; the record adds ds003592's call with the log-linear fit. In every one the replica gives tedana 26.0.3's files in both environments. fMRIPrep's own files, made by tedana 25.0.1, differ from tedana 26.0.3's for the reasons the table's note lists, and from LARMORX's default about as much.

{{ ev.table('tedana-t2smap', 'calls') }}

Those differences are tedana's own step between its versions, not a difference of machines. tedana 25.0.1, run here in fMRIPrep's image on fMRIPrep's own call, gives fMRIPrep's files bit for bit in all four curve-fit calls once numpy computes float64 exp and log as it did in fMRIPrep's run:

- with its AVX-512 kernels for the three runs made on this machine (their settings name only OpenBLAS's Haswell kernels);
- with glibc's functions (the AVX-512 kernels off, LARMORX's reference setting) for ds003592's, made on a machine without AVX-512.

With the other kernels the curve fit ends elsewhere in a few voxels (NP-04).

{{ ev.table('tedana-t2smap', 'fmriprep-tedana-25') }}

## The clean room on fMRIPrep's calls {#original-fmriprep}

The six fMRIPrep calls of the clean room's record (fMRIPrep's four, and ds003592's also with `--fittype loglin` and with `--verbose`) are each judged twice by the specification's thresholds: (A) the clean room's `reproduce` against tedana 26.0.3, and (B) its `fix` against the replica's `fix`. The share of a call's fit voxels judged by the curve fit's objective rather than by value is the (b)/\(c) share. The log-linear call's values are tedana's but for one float32 unit of the combined series.

{{ ev.table('tedana-t2smap', 'fmriprep-calls-original') }}

### ds003592: tedana, the replica and the clean room {#original-ds003592}

The first example's call was given to tedana 26.0.3, to the replica's `fix` and to the clean room in `reproduce` at one thread and in `fix` at eight and at one; the first example shows these same runs of the clean room. The maps shown are the T2* and S0 maps, the RMSE map (no value where fewer than two echoes are good: those voxels are not drawn) and the adaptive mask. The comparisons with tedana and between the two ports' `fix` are judged by the specification's `check.py` (§17.3): value by value within its thresholds and, for 0.305 % of the curve fit's voxels (0.259 % between the two `fix`), by the fit's own objective. The clean room's files are the same at one and eight threads.

{{ ev.example('tedana-t2smap', 'fmriprep-ds003592-curvefit-original') }}

## Every file {#files}

The two calls shown above, file by file: the replica's every value is tedana's, the RMSE map (NaN where fewer than two echoes are good) and the confounds table included, at 1 and 14 threads. Its default, `fix`, changes what the corrections change, and tedana's own runs show how much tedana varies with its kernels, releases, threads and version.

{{ ev.table('tedana-t2smap', 'files') }}

## tedana's own variability {#spread}

The record's spread cases measure how much tedana 26.0.3 varies on one machine when one setting changes:

- numpy's AVX-512 kernels for float64 exp and log (NP-04: Intel's SVML kernels, which numpy uses by default on this CPU; LARMORX's reference is the path without them, decision D2);
- the library releases (SciPy's trust-region method changed between 1.15 and 1.18);
- four threads (tedana's curve fits in four processes);
- its version (25.0.1, in fMRIPrep's image on this machine).

The replica and the clean room give the same bytes at any thread count.

{{ ev.table('tedana-t2smap', 'spread') }}

## Corrections by default {#corrections}

Every defect found in tedana was decided by the register's rules (A: corrected by default; B: refused with a clear error; C: kept and documented; D: measured first). `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives tedana's behaviour, its errors and messages included ([the replica's findings](repo:docs/findings/tedana-t2smap.md)).

fMRIPrep's calls meet TED-05 (the full T2* map uncapped, every call), TED-08 (a failed fit of a voxel with one good echo not marked in the failures map, three of the four curve-fit calls) and the maths entries NP-03 and GLIBC-07, all corrected and named by default. The other entries need inputs or options fMRIPrep does not give.

The clean room's implementers found two more:

- TED-31 (rule B): a run whose adaptive mask removes every voxel, where tedana fails with an `IndexError`, stops with a clear error;
- TED-46 (rule A): a voxel whose observations are all equal, a saturated sample, gets the slope 0 instead of tedana's rounding noise, which makes its T2* 1 ms or 10¹⁶ ms and more. In the curve fit it gets the fit's exact solution: S0 the samples' value, and no decay.

Both ports make every correction by default and name each alike; the clean room's record holds each case's `fix` against the replica's ([the clean room's findings](repo:docs/findings/tedana-t2smap-clean-room.md)).

{{ ev.table('tedana-t2smap', 'corrections') }}

## Speed {#speed}

The clean room is built for speed, and on fMRIPrep's calls it is limited by reading and writing the compressed images: on ds003592's call at one thread its log-linear fit and its curve fit take 0.10 and 0.09 s, and reading the echoes 1.6 s ([the clean room's findings](repo:docs/findings/tedana-t2smap-clean-room.md)).

Its benchmark ([report](repo:docs/benchmarks/tedana-t2smap.md), "The clean-room original") ran tedana, the replica's `fix` and the clean room in both modes on the same calls, the best of two runs at one and eight threads, on a machine shared with other work:

- on the curve-fit calls 2.7 to 3.7 s at one thread, 10 to 15 times tedana's speed, and 1.3 to 2.0 s at eight threads, 19 to 30 times;
- on the log-linear call 3.0 s and 1.5 s, where tedana takes 6.2 s;
- its files the same at one and eight threads in both modes.

The replica's benchmark runs tedana 26.0.3 and the replica on the record's five fMRIPrep calls (fMRIPrep's four and ds003592's with the log-linear fit). It times the whole command (reading, the masks, the fits, the maps, the combination, writing) and checks every `reproduce` run's files against tedana's.

- At 14 threads the replica takes 3.0 to 4.2 times less time than tedana on the curve-fit calls.
- At one thread it takes about as long (0.8 to 1.1 times tedana's speed), because both modes run up to four passes to name the maths entries exactly.
- On the log-linear call, which tedana finishes in 6 s, those passes make it slower.

The chart's factor is the replica's at 14 threads; the clean room's factors are in the table below it.

{{ ev.speed('tedana-t2smap') }}

{{ ev.table('tedana-t2smap', 'speed-original') }}

## Memory {#memory}

The memory rule allows LARMORX at most 10 % above the original's peak plus 8 MiB for the same call. Here the replica needs 44 % of tedana's peak, and the clean room a quarter at one thread (at eight threads it decodes the three echoes at once: 44 %).

{{ ev.table('tedana-t2smap', 'memory') }}

{{ ev.table('tedana-t2smap', 'memory-original') }}

## Random testing {#random-testing}

Random testing runs random valid and invalid multi-echo inputs and option combinations through tedana and LARMORX and compares every output ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it. It is then fixed and kept as a comparison case, registered as a defect of tedana, or reported.

The replica's random-testing run (2026-11-08) was 30 minutes long, and a check of its final build 10 minutes:

{{ ev.table('tedana-t2smap', 'trial') }}

{{ ev.table('tedana-t2smap', 'triage') }}

The clean room's random-testing run (2026-11-11) was 30 minutes long. Each random case was run by tedana, by the clean room in both modes and by the replica's `fix`: (A) the clean room's `reproduce` against tedana, and (B) its `fix` against the replica's, both by the clean room's comparison suite and the specification's thresholds. Every kind of difference, with what it was:

{{ ev.table('tedana-t2smap', 'difftest-original') }}

## Every case {#cases}

Each case of the two records, with what it tests, its command line, its verdict and the reason. Search, filter (or select a segment of a chart above), sort; `#case=<name>` links to one (the clean room's cases are named `original/<case>`).

The clean room's record:

{{ ev.cases('tedana-t2smap', 'original') }}

The replica's record:

{{ ev.cases('tedana-t2smap', 'replica') }}

## Known limits {#limits}

- The clean room's `reproduce` holds tedana's fitted numbers within the specification's thresholds, not bit for bit; the replica is the exact one. SciPy's own floating-point warnings inside its trust-region steps, which tedana prints in degenerate fits, are not part of that contract, and the clean room does not print them (the record's one expected divergence).
- Both ports read NIfTI-1 and -2 (`.nii`, `.nii.gz`, pairs), ANALYZE 7.5 and MGH. The other formats nibabel reads (AFNI, MINC, PAR/REC) are refused with a clear message, a documented gap.
- The replica's log lines are tedana's. Python's warnings name the replica's own place instead of tedana's installed file, its progress bars are its own, and `dataset_description.json` describes the replica and the library releases it reproduces where tedana describes its Python (decision D6).
- Both reproduce tedana 26.0.3, not 25.0.1, fMRIPrep 25.2.6's: the step between the two is measured above, not reproduced.
- The records hold fMRIPrep's calls on its three multi-echo fMRIPrep runs. The replica's full comparison and the long random-testing runs come in the final validation phase.
- The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output.

## History {#history}

- **2026-11-08**: the replica, translated from tedana 26.0.3 with numpy's, SciPy's, nibabel's and nilearn's arithmetic; tedana's defects TED-01 to TED-18 found and the maths entries NP-03, NP-04 and GLIBC-07, each corrected by default, refused with a clear error or kept by rule; its random-testing run, 3,886 random cases in 30 minutes, and the 10-minute check of its final build ([the roadmap](/roadmap/)).
- **2026-11-09**: the fMRIPrep runs of ds000210 and ds000258 made again with OpenBLAS's Haswell kernels.
- **2026-11-11 and 12**: the clean room, written from [specs/t2smap.md](repo:specs/t2smap.md), tedana's documentation, the papers it names and runs of tedana and of the replica; TED-31 and TED-46 found and corrected by both ports; its record, its random-testing run of 2026-11-11 (1,742 random cases in 30 minutes) and its benchmark; the replica's record made again, ANALYZE and MGH images read ([the roadmap](/roadmap/)).
- **2026-11-13**: the clean room shown in the three worked examples that showed tedana and the replica only (its runs of ds000258's call made then; ds003592's are those of its own example).
