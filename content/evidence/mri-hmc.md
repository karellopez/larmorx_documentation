---
title: Head-motion correction
kicker: Evidence · FSL
lede: >-
  Head-motion correction estimates, for every volume of a BOLD run, the rigid transform that
  aligns it to a reference volume, in mcflirt's coarse-to-fine schedule, and optionally resamples
  the run; fMRIPrep runs FSL's `mcflirt` with its BOLD reference and keeps the matrices. The
  replica of mcflirt (`larmorx-nc`) gives FSL 6.0.7.23's files, messages and exit status byte for
  byte in all 205 of its compared cases, out of 237, fMRIPrep's calls among them, and FSL
  6.0.7.17's in all 173 of its full comparison's, out of 194. The clean room (`larmorx`,
  `lx.mri.hmc`) is within its record's thresholds in 145 of its 149 compared cases, out of 170;
  the other 4 are expected divergences, each with its reason. On fMRIPrep's own run its motion
  estimates stay within mcflirt's own variability, and it runs 1.2 to 2.3 times as fast as
  mcflirt on one thread, 4.9 to 9.4 times on 12.
description: >-
  How LARMORX's two ports of FSL's mcflirt, a replica and a clean room, compare with FSL 6.0.7.17
  and 6.0.7.23: fMRIPrep's mcflirt command on a real run to inspect, the six parameters and the
  framewise displacement over the run against mcflirt's own variability, the corrections, every
  case of the three records with its verdict, random testing, and the speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx-nc</code> <span class="port-licence">FSL Licence: non-commercial use only</span>: translated from FSL 6.0.7.17's source, and following FSL 6.0.7.23's since the version update of 2026-10-29; it runs as a separate program</li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crate <code>larmorx-mri</code>, written from <a href="{{ repo('specs/mcflirt.md') }}">specs/mcflirt.md</a> and runs of mcflirt, without FSL's source</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span> (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>); clean room <span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/fsl-mcflirt-replica.md') }}">standard comparison</a> (FSL 6.0.7.23) and <a href="{{ repo('docs/validation/fsl-mcflirt-replica-full.md') }}">full comparison</a> (FSL 6.0.7.17) · the clean room's: <a href="{{ repo('docs/validation/mri-hmc.md') }}">standard comparison</a> (FSL 6.0.7.23) · benchmark <a href="{{ repo('docs/benchmarks/mri-hmc.md') }}">mri-hmc</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/mri-hmc.md') }}">mri-hmc</a></dd>
</dl>

## What is compared {#what-it-is}

Head-motion correction estimates, for every volume of a BOLD run, the rigid transform that aligns it to a reference volume, in mcflirt's coarse-to-fine schedule, and optionally resamples the run. fMRIPrep runs mcflirt with its BOLD reference and keeps the matrices.

The two ports run beside FSL's mcflirt on the same files with the same arguments: FSL 6.0.7.23's since 2026-10-29, FSL 6.0.7.17's before. fMRIPrep's own matrices are the files it wrote in its run.

```bash
larmorx mri hmc -in bold.nii.gz -out bold_mcf.nii.gz -reffile hmc_boldref.nii.gz -mats -plots
larmorx fsl mcflirt -in bold.nii.gz -out bold_mcf.nii.gz -reffile hmc_boldref.nii.gz -mats -plots
```

Both commands run `lx.mri.hmc`; the second is mcflirt's own name for it.

```python
import larmorx as lx

hmc = lx.mri.hmc("sub-01_task-rest_bold.nii.gz", reference="hmc_boldref.nii.gz",
                 resample=False, n_threads=8)
# hmc.matrices: the (N, 4, 4) FSL matrices, as mcflirt's MAT_* files
# hmc.implementation: which port ran
```

The calls above leave `implementation` at `"auto"`. The [API page](repo:docs/api/mri-hmc.md) describes every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

FSL comes under the FSL Licence, which allows non-commercial use only. So LARMORX has two ports of its FSL programs. The replica is translated from mcflirt's source and lives in its own package, `larmorx-nc`. The clean room is in `larmorx` itself, written from mcflirt's behavioural specification ([specs/mcflirt.md](repo:specs/mcflirt.md)) and runs of mcflirt as a black box.

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). On the command line, `larmorx --implementation clean-room fsl mcflirt ...` does the same from the next release; in 0.1.0rc1 it is the environment variable `LARMORX_IMPLEMENTATION`. `auto` takes the replica when `larmorx-nc` is installed, else the clean room. `larmorx-nc` is installed by name, `pip install larmorx-nc`, or with `pip install "larmorx[all]"`, so that its non-commercial licence is accepted knowingly ([the packages](/concepts/#packages)).

**The C library's last digits (since 2026-11-04).** With `-cost mutualinfo` and `-cost normmi`, mcflirt's cost takes logarithms (`logf`) from glibc, the C library of Linux, whose results are now and then one unit in the last place from the exact value rounded once. LARMORX computes them correctly rounded, the same on every platform.

- Since 2026-11-04 the clean room's `reproduce` computes them exactly as glibc 2.35 does, with LARMORX's versions of glibc's functions (`larmorx_core::math`), and its `fix` correctly rounded.
- GLIBC-07 in the [register](repo:docs/findings/upstream-defects.md) is named nowhere there, as decided on 2026-11-04: whether a fit moved with such last bits cannot be told without running it twice.
- fMRIPrep's calls use the normalised correlation, which calls neither, so the example below is unchanged.
- Three cases of the record moved by thousandths of a millimetre, their verdicts unchanged: `-cost mutualinfo` toward mcflirt (0.0048 → 0.0047 mm, the 95th percentile of the matrices' RMS deviation), and `-cost normmi` the other way (0.0108 → 0.0126 mm of its 0.1 mm), the size of the fit's own sensitivity to those last bits (its two modes part by 0.0109 mm). So did random testing's `normmi` case.

**The weighted correlation's count (since 2026-11-07).** fMRIPrep's cost, the normalised correlation with mcflirt's edge weights, divides by the count of the points it weighs. The specification's answer of 2026-11-06 ([specs/mcflirt.md](repo:specs/mcflirt.md) §6.4) says mcflirt adds each point's weight to a running total as the point is visited. The clean room had added each row's total at the row's end, which rounds otherwise where the weights are fractional (near the volume's bounds).

- With the count per point, the clean room's evaluated matrices are mcflirt's for longer on every recorded run traced ([findings](repo:docs/findings/mri-hmc-clean-room.md), "The count per point"), and the example below moves within mcflirt's band.
- Its record, made again with it ([the record](repo:docs/validation/mri-hmc.md)), holds 145 of its compared cases within the thresholds.
- Two synthetic runs end just beyond the thresholds made for real BOLD runs, each within mcflirt's own spread on that run, measured by moving its inputs in their last bits (*expected divergences*, each with its numbers in the case explorer): `syn/orientation/ras-unflipped/reffile`, and the ramp `syn/content/ramp/reffile`, which only one translation can align.
- The `leastsquares` cost is FLIRT's since the same day (three single-precision levels, the specification's appendix A).

## The verdicts at a glance {#verdicts}

The replica is a translation of mcflirt's own source, so the question for it is whether it gives mcflirt's bytes: every output file, the exit status and both message streams, compared with mcflirt as built (with the C library's maths it calls on Linux).

Since the version update of 2026-10-29 the replica follows FSL 6.0.7.23, and its standard comparison runs against it (the chart below; [the record](repo:docs/validation/fsl-mcflirt-replica.md)): 137 runs recorded again with 6.0.7.23's mcflirt, fMRIPrep's calls and the edge cases, with new ones for 6.0.7.23's zstd and bzip2 formats, for random testing's finds and for the 33 failure cases of specs/mcflirt.md §14.1. 205 of its 205 compared cases are bit-identical, and in 32 both fail alike.

{{ ev.agreement('mri-hmc', 'replica-23') }}

Each case also says what changed between FSL's two versions, and why:

- 127 of the 137 recorded runs give the same bytes.
- `-sinc_final` and `-nn_final` now resample trilinearly in mcflirt itself (FSL-59, which the replica reproduces and corrects by default).
- In five cases the last bits of a matrix change, because 6.0.7.23 inverts its 4 × 4 matrices through LAPACK (Armadillo 14.2.1 on OpenBLAS 0.3.33). The replica follows that arithmetic since the version update's third part (2026-10-29), checked bit for bit against FSL's own library on 30.2 million seeded matrices: those five, expected divergences of at most 10⁻¹² until then, are bit-identical now.
- OpenBLAS chooses its kernels by the CPU, and on CPUs with AVX-512 they fuse multiplications and additions, so FSL's own last bits depend on the machine (FSL-64). The 137 runs were recorded again on the kernels of CPUs without AVX-512, the order the replica follows on every platform. One of them changed: the relative rms of identical volumes, 8.07 × 10⁻¹⁵ against 7.98 × 10⁻¹⁵ mm.

The replica's full comparison, against FSL 6.0.7.17 (the chart below; [the record](repo:docs/validation/fsl-mcflirt-replica-full.md)), runs the 137 recorded mcflirt runs, fMRIPrep's own mcflirt calls on the twelve fMRIPrep runs that have BOLD runs, and edge cases made for it. fMRIPrep's 22 calls include the data panel's: a child's extreme motion, 1.5 T, multiband-8 with 600 volumes, multi-echo, a stroke, a glioma; fMRIPrep's 4,517 matrices are identical too. The edge cases are the failure cases, every output type, `-gdt`, `-verbose 20`, histogram costs with few bins and moving phantoms. 173 of its 173 compared cases are bit-identical, and in 21 both fail alike. The four cases only the full comparison runs (fMRIPrep's 280-volume multiband run of ds005454 and three `-sinc_final` and `-stages 4` runs) wait for the final validation phase against 6.0.7.23.

{{ ev.agreement('mri-hmc', 'replica') }}

Two of the data panel's calls, and 58 of the first 59 differences random testing found, came from one constant of the C library's `atanf` in the replica's translation. `aT[0]` had been taken from fdlibm's source comment (`0x3eaaaaaa`) instead of its decimal value (`0x3eaaaaab`, the value glibc holds), which moved one rotation angle by one unit in the last place (on ds002422's rest run, in 1 of mcflirt's 600 rotation decompositions). With it corrected, every one of them is bit-identical; the last difference was a missing FSL-08 notice, now given ([findings](repo:docs/findings/fsl-mcflirt.md)).

The clean room is written without mcflirt's source, so it is not expected to give mcflirt's bits. The question for it is whether its estimates differ from mcflirt's by no more than mcflirt's own differ when its input changes imperceptibly. mcflirt is deterministic, so that variability is measured by perturbing its input: noise of half a quantisation step (three realisations) and the volumes in reverse order ([the record](repo:docs/validation/mri-hmc.md)).

- A case is *within the original's variability* when every compared estimate is inside that band: 33 of them.
- It is *open* when it exceeds the band, or when the band is not measured for that case (the options and synthetic series), even though it meets the record's thresholds: 112 ([below](#open)).
- 4 are *expected divergences*: the two synthetic runs above, and two of random testing's phantoms with large motion, whose estimates end in other minima than mcflirt's, aligning the series as well or better.
- In 21 both fail alike.

{{ ev.agreement('mri-hmc', 'original') }}

The clean room follows FSL 6.0.7.23 too since 2026-10-29, and its record runs against 6.0.7.23's recorded runs:

- `-sinc_final` and `-nn_final` as asked by default, and trilinear in `reproduce` (FSL-59);
- every output type, the zstd and bzip2 ones included, files read by their content and names completed as FSL completes them, and FSL-60's renamed names in `reproduce`;
- `-cost mutualinfo` and `normmi` computed exactly as the specification's appendix B describes them. With `-fudge -stages 1` they give mcflirt's evaluated matrices, evaluation by evaluation, on 22 of 30 random phantoms. On the 169 phantoms random testing had found for these costs, the corrected series are as well aligned as mcflirt's (median ratio of the temporal standard deviations 1.000; `normmi` was 1.051 before).

## A worked example: fMRIPrep's mcflirt {#example}

fMRIPrep's own call on OpenNeuro ds000005's first run: its command, its BOLD and its HMC reference, given to FSL 6.0.7.17's mcflirt and to LARMORX's two ports, and to FSL 6.0.7.23's mcflirt with both ports' runs compared with it. *FSL mcflirt 6.0.7.23 − 6.0.7.17* is mcflirt's own step: the same bytes on this command. The chart under the viewer has the six parameters and the framewise displacement of every volume, and each port's deviation from mcflirt's matrix next to mcflirt's own band: the replica's is zero at every volume.

{{ ev.example('mri-hmc', 'fmriprep-hmc') }}

The clean room's three runs of this call were made again on 2026-11-05 with the clean-room catch-up's build, mcflirt's runs and its band kept. Since then the clean room takes the centres of mass as mcflirt's blocked sums (specs/mcflirt.md §6.1), prints mcflirt's warning where a volume's total is 0, and takes `atan2` from LARMORX's own maths ([findings](repo:docs/findings/mri-hmc-clean-room.md)). They were made again on 2026-11-07 with the correlation's count per point ([above](#ports)).

## Every case {#cases}

Each case of the three records, the clean room's against FSL 6.0.7.23 and the replica's against FSL 6.0.7.17 and 6.0.7.23 (a column each), with what it tests, its command line, each port's verdict and the reason. The replica's edge cases and fMRIPrep's calls are cases of their own. Search, filter by category or verdict (or select a segment of a chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('mri-hmc') }}

## Speed {#speed}

mcflirt runs on one thread; the clean room runs on as many as it is given, with the same result.

- On ds000005's run (240 volumes) the clean room takes 26.6 s on one thread against mcflirt's 30.7 s, and 6.2 s on 12.
- On ds006010's multiband run (113 volumes of 96 × 96 × 69) it takes 23.6 s against 54.5 s, and 5.8 s on 12.
- On ds000258's run (239 volumes) it takes 33.2 s against 39.2 s, and 7.5 s on 12.

These timings come from [the benchmark report](repo:docs/benchmarks/mri-hmc.md) of 2026-10-10: the whole command, the median of three runs after a warm-up (mcflirt one run), on an Intel Core i7-8750H with 12 logical CPUs, against FSL 6.0.7's mcflirt.

{{ ev.speed('mri-hmc') }}

## Corrections by default {#corrections}

The clean room's record names its corrections where they change a result: FSL-01 (the last volume not initialised from the previous one), FSL-03, FSL-05, FSL-06, FSL-07, FSL-08, FSL-09, FSL-10, FSL-13, FSL-14, FSL-20, FSL-21, FSL-59, FSL-65 and FSL-66. Each is corrected by default, `fix`, with `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) giving mcflirt's behaviour, the mode the comparison runs in ([register](repo:docs/findings/upstream-defects.md)). The worked example shows what they change on fMRIPrep's run.

- Since 2026-10-30 the clean room handles FSL-20, FSL-21, FSL-65 and FSL-66 as its specification says (outputs that cannot be written, impossible bin counts): the record's 33 failure cases of specs/mcflirt.md §14.1.
- Without `FSLOUTPUTTYPE`, mcflirt writes the `.mat` files and stops at its first image with FSL's message (FSL-11), and so does the clean room in `reproduce`; its `fix` writes every output, the images as `.nii.gz` ([`syn/motion/small/no-fsloutputtype`](#case=syn/motion/small/no-fsloutputtype)).

The replica corrects the same defects the same way by default, and three more that its translation found:

- `-gdt` (FSL-04): refused; `reproduce` registers the gradient images as mcflirt does;
- a `.mat` directory that cannot be created (FSL-20): mcflirt exits with status 0 having written nothing more; an error;
- the histogram costs with fewer than 8 bins (FSL-21): the first stage has no bins, the matrices are arbitrary, and `corratio` corrupts its heap and aborts; refused.

`reproduce` gives mcflirt's bytes, aborts included. FSL 6.0.7.23 adds one: `-sinc_final` and `-nn_final` are resampled trilinearly (FSL-59: each volume keeps the interpolation it was first read with); the replica uses the method asked for by default, and 6.0.7.23's trilinear resampling in `reproduce`. An image name holding `.img` or `.hdr` before its extension makes 6.0.7.23 open another file (FSL-60): corrected the same way. The clean room corrects FSL-59 and FSL-60 alike since 2026-10-29 (FSL-60 on its command line; its Python API opens the name given).

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a case of the record, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/evidence/mri-hmc/', 'mri-hmc') }}

The clean room's random-testing run after the catch-up (2026-11-05, after its change of the centres of mass), 30 minutes long against FSL 6.0.7.23's mcflirt, each difference in one category:

{{ ev.table('mri-hmc', 'trial-catchup') }}

{{ ev.table('mri-hmc', 'trial-catchup-triage') }}

## What is open {#open}

{{ ev.table('mri-hmc', 'open') }}

- No case misses its threshold. Until the record of 2026-11-07 one did: `real/ds003345/default` (mcflirt's defaults, the middle volume as reference), whose framewise displacement correlated with mcflirt's at r = 0.9885 where mcflirt's own band reaches 0.9893. With the correlation's count per point it correlates at r = 0.9907, within the band.
- mcflirt's variability is measured for fMRIPrep's command on the nine real runs, for mcflirt's defaults on most of them and for a few synthetic series. The options and the other synthetic series are held to the record's fixed thresholds only, so they stay open until their band is measured.
- The replica's full comparison against FSL 6.0.7.23 waits for the final validation phase; the cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output.

## History {#history}

- **2026-10-10**: the clean room, experimental, and its benchmark against FSL 6.0.7's mcflirt.
- **2026-10-25**: the replica, translated from FSL 6.0.7.17's source, and its full comparison, 173 of 173 compared cases bit-identical; the first long random-testing run, whose differences were all one constant of `atanf` and a missing FSL-08 notice.
- **2026-10-29**: both ports follow FSL 6.0.7.23 (FSL-59 to FSL-63 registered); the replica follows FSL's matrix library bit for bit; the clean room's `-cost mutualinfo` and `normmi` computed exactly.
- **2026-10-30**: the clean room handles FSL-20, FSL-21, FSL-65 and FSL-66 as its specification says; the replica's standard comparison gains the 33 failure cases of specs/mcflirt.md §14.1.
- **2026-11-04**: the clean room's `reproduce` computes `logf` as glibc 2.35 does.
- **2026-11-05**: the clean-room catch-up: the centres of mass as mcflirt's blocked sums, 145 of its 149 compared cases within the thresholds then, 3 expected divergences and one case, `real/ds003345/default`, just beyond its band; its random-testing run of 30 minutes.
- **2026-11-07**: the weighted correlation's count per point and FLIRT's `leastsquares`: no case misses its threshold since.
- **2026-11-11**: the clean room's record made again: `syn/motion/small/no-fsloutputtype` is rejected by both (it was an expected divergence), every other case as before.
