---
title: 3dvolreg
kicker: Evidence · AFNI
lede: >-
  `3dvolreg` moves every volume of a series onto a base volume by a rigid-body transformation.
  fMRIPrep's BOLD reference is the median of 20 of a run's volumes once 3dvolreg has aligned
  them. LARMORX has two ports of it, both in `larmorx` itself. The replica gives AFNI 26.3.05's
  bytes, every file 3dvolreg writes, in all 137 compared cases of its record that write
  outputs, out of 190, fMRIPrep's calls included. The clean room is held to its
  specification's limits instead of AFNI's bits, and stays within them in all 185 compared
  cases of its record, out of 251. It runs fMRIPrep's calls 2.8 to 5.2 times as fast as AFNI
  on one thread, and 9 to 15 times on 14.
description: >-
  How LARMORX's two ports of AFNI's 3dvolreg, the replica and the clean room, compare with
  AFNI 26.3.05, AFNI 25.2.09 and fMRIPrep 25.2.6: fMRIPrep's registration of a real BOLD run's
  reference volumes with its motion parameters, the BOLD reference fMRIPrep makes from them, a
  correction by default (AFNI-99: the maximum displacement of a mirrored voxel) on the same
  volumes stored two ways, a child's high-motion run where the clean room comes closest to its
  limits, random testing, the speed of both ports against AFNI, and every case of both records
  with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0, with CC BY 4.0's attribution for the Medical College of Wisconsin's code</span>: translated from AFNI 26.3.05's source; in <code>pip install larmorx</code></li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>, crate <code>larmorx-afni</code>: written from <a href="{{ repo('specs/3dvolreg.md') }}">specs/3dvolreg.md</a>, AFNI's help, Cox and Jesmanowicz's paper (1999) and runs of AFNI 26.3.05 and of the replica, used as black boxes (2026-11-08)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span> (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>); clean room <span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/afni-volreg-replica.md') }}">standard comparison</a> (AFNI 26.3.05) · the clean room's: <a href="{{ repo('docs/validation/afni-volreg-original.md') }}">standard comparison</a> (AFNI 26.3.05) · benchmark <a href="{{ repo('docs/benchmarks/afni-volreg.md') }}">afni-volreg</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/afni-volreg.md') }}">afni-volreg</a></dd>
</dl>

## What is compared {#what-it-is}

3dvolreg moves every volume of a series onto a base volume (the first, by default) with a rigid-body transformation: three rotations and three shifts. For each volume it solves a weighted least-squares problem linearised about the current estimate: the volume against the base and the base's derivatives with respect to the six parameters, weighted by the base's own values. It resamples, and repeats until the parameters stop changing. `-twopass` first registers blurred copies, starting from a coarse search over shifts and rotations, and refines from there. The resampling is done by four shears, each a shift of rows, on a volume zero-padded by `-zpad` voxels. The interpolation is Fourier (`-Fourier`, the most accurate, fMRIPrep's), heptic (the default), quintic, cubic, linear or nearest-neighbour. Besides the registered series it writes, on request, the parameters (`-1Dfile`, `-dfile`), the matrices (`-1Dmatrix_save`), the maximum displacement of a brain voxel per volume (`-maxdisp1D`) and fields of displacements (`-savedisp`). It can apply saved matrices, shift each slice in time first (`-tshift`), and register to another dataset's grid or motion (`-gridparent`, `-rotparent`).

fMRIPrep calls it for every BOLD reference. niworkflows' RobustAverage (the `gen_avg` node of `hmc_boldref_wf`) takes 20 of a run's volumes (on ds000005's first run, volumes 20 to 39 of 240), clips them and divides them by the global signal's drift. It gives them to 3dvolreg with `-Fourier -twopass -zpad 4`, and takes the median of the registered volumes as the run's reference. sdcflows' PEPOLAR estimator makes its reference averages the same way.

The two ports run beside AFNI 26.3.05's `3dvolreg` and AFNI 25.2.09's on the same files with the same arguments, both AFNI releases the repository's builds, and beside fMRIPrep's build of AFNI in its image; fMRIPrep's own output is the file it wrote in its run.

```bash
larmorx afni 3dvolreg -Fourier -twopass -zpad 4 -prefix registered.nii.gz \
    -1Dfile motion.1D -1Dmatrix_save motion.aff12.1D -maxdisp1D md.1D sliced.nii.gz
```

```python
import larmorx as lx

r = lx.afni.volreg("sliced.nii.gz", **lx.afni.fmriprep_volreg_options())
r.registered, r.parameters, r.matrices, r.max_displacement
```

The calls above leave `implementation` at `"auto"`. The [API page](repo:docs/api/afni-volreg.md) maps every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

3dvolreg's results depend on AFNI library routines copyrighted by the Medical College of Wisconsin, which AFNI 26.3.05 releases under CC BY 4.0. So the replica is part of LARMORX itself (`pip install larmorx`), under the Apache License with CC BY 4.0's attribution ([NOTICE](repo:NOTICE), [licensing](repo:docs/licensing.md)), and runs in the same process. The replica is translated from AFNI's source. The clean room is written without it, from a description of what the program does ([specs/3dvolreg.md](repo:specs/3dvolreg.md)), and runs in the same process too.

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). `auto`, and `larmorx afni 3dvolreg`, take the replica. On the command line, `larmorx --implementation clean-room afni 3dvolreg ...` runs the clean room from the next release; in 0.1.0rc1 it is `LARMORX_IMPLEMENTATION=original`.

**Threads.** The replica follows AFNI's arithmetic step by step. AFNI's 3dvolreg has no parallel loop on this path, and neither has the replica, so its results do not depend on the thread count. The clean room divides the work inside each volume between threads in fixed pieces, so its results are the same bits at any thread count too.

## The verdicts at a glance {#verdicts}

The replica is a translation of AFNI's source, so the question for it is whether it gives AFNI's bytes: the registered series (header and data), every text file 3dvolreg writes, its standard output and error, and its exit status.

{{ ev.agreement('afni-volreg', 'replica') }}

The replica's record runs 190 cases against AFNI 26.3.05 ([the record](repo:docs/validation/afni-volreg-replica.md)). In each of the 137 that write outputs the replica gives AFNI's bytes, every file: the registered series (header and data) and every text file (`-1Dfile`, `-dfile`, `-1Dmatrix_save`, `-maxdisp1D`, `-savedisp`'s datasets). In 21 more neither program writes an output (an existing output, a name with a blank, a directory that does not exist), and both give the same exit status and messages. In 30 AFNI refuses the input and the replica does the same, with AFNI's message and exit status.

Seven of those are AFNI crashing: an option given last without its value, a base whose least squares cannot be set up, a name of 256 bytes, a Fourier rotation that clears a row through a null pointer. There the replica prints AFNI's messages up to the crash and stops with an error instead, an *expected divergence*. So are the two cases where AFNI writes its own dataset format, which LARMORX does not write.

The messages are AFNI's, byte for byte, in all 180 cases that run both programs. fMRIPrep's own outputs of its eight calls (RobustAverage's BOLD reference of six BOLD runs from five fMRIPrep runs, sdcflows' two PEPOLAR averages) are the replica's, every value, and so are those of fMRIPrep's build of AFNI. AFNI 25.2.09 gives 26.3.05's result in all 189 cases it runs: 3dvolreg did not change between the two releases. The Python API gives the command line's outputs in 21 of 21 cases.

The cases cover every interpolation method and `-final`, `-twopass` with its options and coarse searches (the subsampled search of a volume of 120 or more voxels along every axis included), the bases, weights, edging and clipping, `-tshift`, `-rotparent`, `-gridparent` and `-twodup`. They cover every output and data type, oblique and sagittal series, NaN, constant and single volumes, the environment's settings, and every message, exit status and failure case of the command line. Seven cases come from random testing: six from its first run, one from the final build's check. Each case also runs the replica's default, `fix`, where LARMORX corrects AFNI's deterministic defects and names them (below).

The clean room is not a translation: it is written from the specification ([specs/3dvolreg.md](repo:specs/3dvolreg.md)), so the question for it is whether it behaves as AFNI does within the specification's limits (its §14.3). Its exit statuses, files, headers, types, geometry and messages are AFNI's; its numbers cannot all be AFNI's bits. Where two axes have the same voxel size (every EPI with square in-plane voxels), the four shears that rotate a volume can be ordered in ways whose norms tie in exact arithmetic. AFNI decides each tie by its last bits, at every resampling, in a way no specification states. The limits allow for either side of every tie and grow with a volume's rotation, as AFNI's own spread does when its ties are decided the other way (the spec writer measured it on 16 real runs).

{{ ev.agreement('afni-volreg', 'original') }}

The clean room's record runs 251 cases against AFNI 26.3.05 ([the record](repo:docs/validation/afni-volreg-original.md)), and holds each case's `fix` against the replica's `fix` by the same limits. 185 pass, 63 are refused by both with the same messages and exit status, and 3 are expected divergences: AFNI's own `.HEAD/.BRIK` format, twice, and a `-rotparent` attribute that is too short (AFNI-96), which AFNI reads past and the clean room refuses. None fails. 417 of its 1,096 `-1Dfile` lines are AFNI's as text, and its outputs are the same bits at 1, 2, 5 and 14 threads. How close it comes to each limit:

{{ ev.table('afni-volreg', 'limits-original') }}

## In fMRIPrep: a real run's reference volumes {#example}

fMRIPrep's own call on its run of OpenNeuro ds000005 sub-01, given to AFNI 26.3.05, to AFNI 25.2.09, to fMRIPrep's build of AFNI, to the replica and to the clean room. fMRIPrep keeps only the median of the registered volumes (the next example), so the registered series below is what each program writes for that call. The input panels show the run as stored and the volumes 3dvolreg is given. The charts below the viewer are the motion parameters and maximum displacements, volume by volume.

{{ ev.example('afni-volreg', 'fmriprep-volreg') }}

## The BOLD reference fMRIPrep makes from them {#boldref}

{{ ev.example('afni-volreg', 'fmriprep-boldref') }}

## The clean room on fMRIPrep's calls {#original-fmriprep}

The replica's eight calls and two more of the data panel's runs (ds000256's child at the least and at the most motion), on the inputs made again from each fMRIPrep run's node in fMRIPrep's image. AFNI's median is fMRIPrep's own output byte for byte in every one, so the clean room's median is compared with fMRIPrep's output.

{{ ev.table('afni-volreg', 'fmriprep-calls-original') }}

### A child's high-motion run {#ds000256}

ds000256's rest run without feedback moves the most of the data panel's runs (rotations to 4.7°), and the ties weigh most on the volumes that rotate most. Here the clean room comes closest to its limits, 0.68 of one volume's, as close as AFNI's own results come when its ties are decided the other way.

{{ ev.example('afni-volreg', 'fmriprep-ds000256-original') }}

## A correction by default: AFNI-99 {#afni99}

`-maxdisp1D` reports, for each volume, the largest displacement of a voxel inside the base's brain mask, a measure of how much the head moved. AFNI converts the registration's rotation and shift to the dataset's axes with each axis's sign, but takes the voxels' positions without it. So along an axis stored from left to right, posterior to anterior or superior to inferior, it computes the displacement of the voxel mirrored about the axis's centre ([AFNI-99](repo:docs/api/afni-volreg.md#upstream-defects)). The replica's default, `fix`, computes the displacements of the voxels themselves, and names AFNI-99 where a value it prints or writes changes (the messages show two decimals, `-maxdisp1D` three); `reproduce` gives AFNI's numbers.

Below, the volumes of the first example, stored as fMRIPrep gives them (their second axis posterior to anterior) and stored again with that axis reversed. AFNI's maximum displacements depend on the storage order; the replica's do not. The registered volumes are not affected: fMRIPrep, which uses only them, gets the same reference either way. The clean room's `fix` makes the same correction and names it alike (the table under the viewer).

{{ ev.example('afni-volreg', 'afni-99') }}

## Random testing {#random}

The clean room's random-testing run of half an hour (2026-11-08): random moving series with every option, each case run by AFNI 26.3.05, by the clean room in `fix` and in `reproduce` and by the replica's `fix`, and compared as the record compares ([random testing](repo:docs/validation/difftest.md)).

{{ ev.table('afni-volreg', 'trial-original') }}

Most differences come from the ties: random testing's small phantoms with sharp edges make the fits ill-conditioned with respect to them, so AFNI's own result moves with the side each tie takes. For such cases the specification holds the clean room to three times its own spread over twelve seeded tie draws (`LARMORX_VOLREG_TIES=random:<seed>`, a validation switch, not a setting), and a runaway fit (a volume beyond 15° or 20 mm) to its output's structure. A seeded sample of the differences, judged again with the final build, and every kind of difference with what it was:

{{ ev.table('afni-volreg', 'trial-original-retriage') }}

{{ ev.table('afni-volreg', 'trial-original-triage') }}

## Speed {#speed}

The clean room is built for speed. It does the shears by sweeps over planes and the Fourier shears by a batched FFT, runs the coarse search on its support box, and divides the work inside each volume between threads. It is measured against AFNI and the replica on fMRIPrep's calls ([the benchmark report](repo:docs/benchmarks/afni-volreg.md)). On one thread it runs them 2.8 to 5.2 times as fast as AFNI, and on 14 threads 9 to 15 times; the replica, which computes as AFNI does, 1.6 to 3 times.

{{ ev.speed('afni-volreg') }}

{{ ev.table('afni-volreg', 'benchmark') }}

{{ ev.table('afni-volreg', 'benchmark-memory') }}

The replica's first timings (2026-11-06, informal, before the benchmark report):

{{ ev.dots('afni-volreg', 'speed-replica') }}

## Every case {#cases}

Each case of the two records, with what it tests, its command line, its verdict and the reason. Search, filter (or select a segment of a chart above), sort; `#case=<name>` links to one (the clean room's cases are named `original/<case>`).

The replica's record:

{{ ev.cases('afni-volreg', 'replica') }}

The clean room's record:

{{ ev.cases('afni-volreg', 'original') }}

## Corrections by default {#corrections}

Where AFNI has a deterministic defect that changes a result, the replica corrects it by default, `fix`, and warns. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives AFNI's behaviour byte for byte where AFNI's is defined ([the API page's table](repo:docs/api/afni-volreg.md#upstream-defects)).

- `-nocoarserot` turns the coarse rotation search off, as documented (AFNI-86: AFNI reads it as `-noclip`, whose four letters it tests first).
- A byte series is written with its values rounded (AFNI-87: AFNI stretches them to the full byte range).
- Output names of 256 bytes or more are written (AFNI-90: AFNI aborts on a buffer overflow; `-maxdisp1D`'s name is cut at 997 bytes).
- The coarse rotation search's mask always uses its own clip fraction (AFNI-92: `-nomaxdisp` changes it in AFNI), and an empty search region is not taken as the best (AFNI-93).
- A second `-base` is refused (AFNI-95: AFNI keeps the last).
- A Fourier rotation that would clear a row through a null pointer clears it (AFNI-97: AFNI crashes).
- Two messages name the dataset they are about (AFNI-98: AFNI prints `(null)` or a stray argument).
- The maximum displacements are those of the voxels themselves (AFNI-99, above).

Inputs that make no sense stop with a clear error in `fix` and in `reproduce`: an option given last without its value (AFNI-88), a base on which the least squares cannot be set up (AFNI-89), `-coarse 1` on a volume of 120 or more voxels along every axis (AFNI-94: AFNI loops for ever), a `-rotparent` without its centres (AFNI-96). The clean room makes every one of these corrections by default and names them alike; its record holds each case's `fix` against the replica's.

## Known limits {#limits}

The replica's standard comparison holds fMRIPrep's RobustAverage calls on six BOLD runs of five fMRIPrep runs (single-band, multiband, multi-echo, uint16 and float32 storage) and sdcflows' two PEPOLAR reference averages. The full comparison (seven more of the data panel's runs) and long random-testing runs come in the final validation phase.

Sub-brick selectors (`dset[n]`) and AFNI's own `.HEAD/.BRIK` format are refused, as by every LARMORX AFNI program, and LARMORX writes no AFNI header extension, so a LARMORX output cannot serve as a `-rotparent` (AFNI's can). The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output.

The benchmark report's times were measured with other work on the machine beside them, so they are long: the ratios between the programs measured together are the information.

The clean room is held to the specification's limits, not to AFNI's bits, wherever the ties decide them. AFNI is deterministic, so a band of its own variability from imperceptible changes of its input (as for mcflirt) comes in the final validation phase, with the clean room's full comparison and long random-testing runs.

## History {#history}

- **2026-11-06**: the replica's first timings, informal.
- **2026-11-07**: the replica's record, 190 cases against AFNI 26.3.05.
- **2026-11-08**: the clean room, written from specs/3dvolreg.md; its record (251 cases), its random-testing run of half an hour and the benchmark report.
