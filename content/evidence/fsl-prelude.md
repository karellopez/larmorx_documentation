---
title: prelude
kicker: Evidence · FSL
lede: >-
  `prelude` is FSL's phase unwrapping (PRELUDE, Jenkinson 2003). A phase image is known only up to
  whole cycles of 2π, and prelude finds the cycles, region by region, that make it vary smoothly;
  fMRIPrep runs it for every phase-difference field map. The replica (`larmorx-nc`) gives FSL
  6.0.7.23's files, messages and exit status byte for byte in 67 of its 68 compared cases, out of
  88, fMRIPrep's seven calls among them. In the other, a complex128 image, FSL's values come from
  memory it never wrote, and the exit status, messages and file names are compared. The clean room
  (`larmorx`) gives FSL's files, messages and exit status byte for byte in 134 of its 138 compared
  cases, out of 166, fMRIPrep's seven calls among them; in the other 4, FSL's values come from
  memory it never wrote. It unwraps fMRIPrep's two large calls 97 and 211 times as fast as FSL on
  one thread, and a large generated map 610 times.
description: >-
  How LARMORX's two ports of FSL's prelude, a replica and a clean room, compare with FSL 6.0.7.23:
  fMRIPrep's seven phase-unwrapping calls on four fMRIPrep runs with fMRIPrep's own outputs, two
  corrections by default on real phase maps (a NaN first value, the ramps' last slice), a synthetic
  phase whose truth is known, every case of both records with its verdict, both ports'
  random-testing runs with the clean room's triage, and the speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx-nc</code> <span class="port-licence">FSL Licence: non-commercial use only</span>: translated from FSL 6.0.7.23's source (fsl-fugue 2603.0, with newimage's complex reader); it runs as a separate program</li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crate <code>larmorx-fsl</code>, written from <a href="{{ repo('specs/prelude.md') }}">specs/prelude.md</a>, Jenkinson's paper, FSL's usage text and runs of FSL 6.0.7.23, without FSL's source (2026-11-06 and 07)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--experimental">experimental</span>; clean room <span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/fsl-prelude-replica.md') }}">standard comparison</a> (FSL 6.0.7.23) · the clean room's: <a href="{{ repo('docs/validation/fsl-prelude.md') }}">standard comparison</a> (FSL 6.0.7.23) · benchmark <a href="{{ repo('docs/benchmarks/fsl-prelude.md') }}">fsl-prelude</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/fsl-prelude.md') }}">fsl-prelude</a></dd>
</dl>

## What is compared {#what-it-is}

A gradient-echo field map measures the off-resonance field as a phase. The phase difference between two echoes is proportional to the field, but the scanner stores it only modulo 2π. So wherever the field is strong, the stored phase jumps by a whole cycle between neighbouring voxels. Unwrapping adds back the missing cycles.

prelude (*Phase Region Expanding Labeller for Unwrapping Discrete Estimates*; M. Jenkinson, Fast, automated, N-dimensional phase-unwrapping algorithm, Magnetic Resonance in Medicine 49:193–197, 2003) works in three steps:

- it splits the phase range into `-n` intervals (8 by default) and labels the connected regions of voxels whose phase falls in the same interval inside a mask;
- it merges the regions two at a time. For each pair of touching regions it sums the phase differences across their boundary. From these sums follow the whole number of cycles that best joins the two regions, and how well it does: a measure that grows with the boundary's size and with how close the joining is to a whole number of cycles. The pair with the largest measure is merged first: the voxels of one region move by that number of cycles, and the merged region's boundaries with its other neighbours are summed again;
- when one region remains, every voxel holds its phase plus its region's whole cycles.

The mask is the given one (`-m`), or the magnitude's voxels above a threshold (`-t`, by default a tenth of the way from the 2nd to the 98th percentile), kept to its largest connected part. The labels are 3D, or 2D slice by slice for images wider than 64 voxels or with `--labelslices`. `-s` unwraps each slice on its own and joins the slices after. `--removeramps` removes the phase's linear ramp along each axis before unwrapping and restores it after.

Its input is a phase and a magnitude (`-p`, `-a`), or a complex image (`-c`). A phase from 0 to 2π is rewrapped to [−π, π] first, and a phase spanning more than 3π is refused. Besides the unwrapped phase it writes, on request, the mask (`--savemask`), the regions' labels (`-l`) and the phase as read (`-r`).

fMRIPrep calls prelude for every phase-difference field map, in sdcflows' phase-difference workflow (`fmap_preproc_wf/<estimator>/phdiff_wf/prelude`). sdcflows first rescales the scanner's phase difference to radians from its minimum and maximum (or subtracts two phase images, each rescaled), clips the magnitude and extracts the brain. It then runs `prelude --abs=<magnitude> --mask=<brain mask> --phase=<phase difference in rad> --unwrap=<out>`, and turns the unwrapped phase into the field in Hz: divided by 2π and by the echo-time difference.

The two ports run beside FSL 6.0.7.23's `prelude` on the same files with the same arguments. fMRIPrep's own outputs are the files it wrote in its runs, with prelude in fMRIPrep 25.2.6's image.

```bash
larmorx fsl prelude --abs=magnitude --mask=brainmask --phase=phasediff_rad --unwrap=unwrapped
larmorx fsl prelude -c complex -o unwrapped --savemask=mask -l labels --removeramps -v
```

The first is fMRIPrep's call. The second unwraps a complex image with its ramps removed, saves the mask and the regions' labels, and prints every message.

```python
import larmorx as lx

res = lx.fsl.prelude("phasediff_rad.nii.gz", "magnitude.nii.gz", mask="mask.nii.gz")
# res.unwrapped: an lx.Image, float32, in radians
res = lx.fsl.prelude(complex_image="complex.nii.gz", remove_ramps=True,
                     save_mask=True, save_labels=True)
# res.mask and res.labels: the mask and the regions' labels
```

The calls above leave `implementation` at `"auto"`. The [API page](repo:docs/api/fsl-prelude.md) describes every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

FSL comes under the FSL Licence, which allows non-commercial use only. So LARMORX has two ports of its FSL programs. The replica is translated from FSL's source and lives in its own package, `larmorx-nc` (`pip install larmorx-nc`). The clean room is in `larmorx` itself. It is written without FSL's code, from prelude's behavioural specification ([specs/prelude.md](repo:specs/prelude.md)), Jenkinson's paper, FSL's usage text and runs of FSL 6.0.7.23 as a black box.

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). On the command line, `larmorx --implementation clean-room fsl prelude ...` does the same from the next release; in 0.1.0rc1 it is the environment variable `LARMORX_IMPLEMENTATION`. `auto`, and `larmorx fsl prelude`, take the replica when `larmorx-nc` is installed, else the clean room.

The replica follows FSL 6.0.7.23. It runs none of FSL's programs and needs no FSL installation. It keeps FSL's merging order exactly: the same boundary sums, the same arithmetic in the same order. Only its bookkeeping of the regions and their boundaries is faster (ordered sets).

The clean room has every option, message, exit status and failure case, and the defects with their switches; its record holds every file prelude writes to FSL's bits (the specification's threshold, [below](#verdicts)). It is built for speed:

- where FSL looks for the next merge by scanning every boundary sum, for the members of the region that joins by scanning every region, and for its neighbours by scanning every region number, the clean room keeps the sums in slots the merges reuse, an indexed heap of the candidate merges keyed by their measure and pair, each region's list of sums and a weighted union-find of the regions' whole cycles. So a choice costs a logarithm, and a merge the neighbours of the region that joins;
- it makes FSL's choices in FSL's order with FSL's arithmetic, so the bits are FSL's;
- the linear parts (the mask's threshold and its largest part, the regions, the ramps, reading and writing) run on the call's threads in fixed chunks, so the result is the same bits at any thread count;
- it holds no copy of the phase where none is needed.

## The verdicts at a glance {#verdicts}

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes: every file prelude writes (each image's header and data: the unwrapped phase, the mask, the labels, the raw phase), its standard output and error, and its exit status.

{{ ev.agreement('fsl-prelude', 'replica') }}

The replica's record runs 88 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-prelude-replica.md)):

- **Bit-identical, 67.** FSL's files byte for byte, with FSL's messages and exit status.
- **Rejected by both, 20.** FSL refuses the input or stops, and the replica does the same, with the same message and exit status.
- **Expected divergence, 1.** FSL reads a complex128 image with no width, so its values come from memory it never wrote (FSL-265). The exit status, messages and file names are compared.

The cases cover:

- fMRIPrep's seven calls on four fMRIPrep runs, fMRIPrep's own outputs the same too, and the data panel's two other phase-difference maps;
- every option: phase and magnitude, or a complex image in both byte orders and widths; the mask and its threshold; 3D and 2D labels and unwrapping; the phase intervals; series with `--start` and `--end`; the saved mask, labels and raw phase; the ramps; `-v`'s messages;
- every output type, and NaN values in the magnitude and the phase;
- every message, exit status and failure case of the command line.

Each case also runs the replica's default, `fix`, where LARMORX corrects FSL's deterministic defects and names them ([below](#corrections)).

The clean room is written without FSL's source, so its record holds it to the thresholds of [specs/prelude.md](repo:specs/prelude.md) §11:

- FSL's exit status, standard output and error, and the files' names;
- in `reproduce`, every file prelude writes bit for bit: each image's header whole, its extension bytes included, but `descrip`, and its data;
- in `fix`, its default, the replica's `fix` the same, and the same defects named. Where GLIBC-07 is named ([below](#corrections)), the unwrapped phase must keep the replica's whole cycles on at least 99.9 % of the mask's voxels.

Each case's verdict is read from what the record measures.

{{ ev.agreement('fsl-prelude', 'original') }}

The clean room's record runs 166 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-prelude.md)): the replica suite's 88 cases, with the clean room standing in for the replica's program and FSL's runs served by the cache of the original's runs; 77 of its own (`orig-`: the specification's validation plan on generated inputs, every option, image type, orientation, series, complex image, NaN, output type and failure, and fMRIPrep's seven calls run three ways); and a permanent case of random testing. By what each case measures:

- **Bit-identical, 134.** FSL's files byte for byte, with FSL's messages and exit status. fMRIPrep's seven calls are among them, each also against fMRIPrep's own output.
- **Rejected by both, 28.** FSL refuses the input or stops, and the clean room does the same.
- **Expected divergences, 4.** FSL reads values from memory it never wrote: a complex128 image (FSL-265), twice, and an image that is not complex given to `-c` (FSL-263), twice. The exit status, messages and file names are FSL's; the values are not compared.

In `reproduce`, 282 of 282 files of its own cases are FSL's headers and data bit for bit. In `fix`, 252 of 252 are the replica's `fix` bit for bit. On the 5 complex images whose phase it computes with the correctly rounded arctangent (GLIBC-07, [below](#corrections)), the unwrapped phase keeps the replica's whole cycles on every voxel of the mask.

## In fMRIPrep: the phase differences of four fMRIPrep runs {#fmriprep}

fMRIPrep's seven prelude calls were given to FSL 6.0.7.23 (the record's runs, served by the cache of the original's runs), to the replica in `reproduce` and in `fix`, and to the clean room in `reproduce` at 14 threads and at one and in `fix`. fMRIPrep's own output stands beside them: prelude in fMRIPrep's image. Every comparison gives the same bytes. The first table counts what unwrapping did in each call. The second gives the clean room's comparisons and the benchmark's seconds.

{{ ev.table('fsl-prelude', 'fmriprep-calls') }}

{{ ev.table('fsl-prelude', 'fmriprep-calls-original') }}

### ds005454: a GRE phase difference {#ds005454}

The input panels are what prelude is given: the phase difference wrapped into 0 to 2π, the magnitude, and the brain mask drawn over the magnitude. The viewer opens where unwrapping added the most cycles in its slice. The replica's and the clean room's differences from FSL and from fMRIPrep's own output are zero everywhere, at 14 threads and at one.

{{ ev.example('fsl-prelude', 'fmriprep-ds005454') }}

### ds002603: a Philips phase difference at 2 mm {#ds002603}

{{ ev.example('fsl-prelude', 'fmriprep-ds002603') }}

### ds002422: two phase differences at 1.5 T {#ds002422}

The data panel's 1.5 T subject has two phase-difference maps, on different grids, each unwrapped by its own call.

{{ ev.example('fsl-prelude', 'fmriprep-ds002422-run01') }}

{{ ev.example('fsl-prelude', 'fmriprep-ds002422-run02') }}

### ds001600: three field-map protocols {#ds001600}

ds001600 holds several field-map protocols of one subject. Two of them store two phase images, which sdcflows subtracts before prelude (`acq-v1`, `acq-v2`); one stores a phase difference (`acq-v4`).

{{ ev.example('fsl-prelude', 'fmriprep-ds001600-v1') }}

{{ ev.example('fsl-prelude', 'fmriprep-ds001600-v2') }}

{{ ev.example('fsl-prelude', 'fmriprep-ds001600-v4') }}

## A NaN first value, and a correction by default {#fsl272}

FSL takes the phase's maximum and minimum from its first value on. So a phase map whose first value is NaN (the first voxel of a masked or divided map) gets a NaN maximum and minimum, and both the range check and the rewrap to [−π, π] are skipped (FSL-272). A phase from 0 to 2π is then unwrapped in other intervals, and some regions come out whole cycles wrong relative to the rest.

It was measured before deciding (rule D): fMRIPrep's seven maps and a synthetic one, each moved to [0, 2π) with its first value NaN. Seven of the eight came out whole cycles wrong in some regions.

- The replica's default, `fix`, takes the extrema over the values that are numbers. That gives what FSL gives for the same map without the NaN. Its `reproduce` gives FSL's bytes.
- The clean room does the same: its `reproduce` gives FSL's bytes with the NaN, and its `fix` FSL's result without it (*clean room, fix − FSL prelude 6.0.7.23 without the NaN*, zero everywhere).

Below, ds002603's map so changed. Compare *FSL prelude with the NaN − FSL without it* (the defect) with *replica, fix − FSL prelude 6.0.7.23 without the NaN* (the correction).

{{ ev.example('fsl-prelude', 'fsl272') }}

## The ramps' last slice, and a correction by default {#ramps}

With `--removeramps`, FSL's loops stop one column, row and slice short. So the last slice is unwrapped with its ramp while the rest is unwrapped without it, and an image of one slice gets no ramp removed at all (FSL-261). The replica's `fix` takes every column, row and slice.

fMRIPrep does not ask for the ramps' removal. Below, its call on ds002422's second map, whose brain mask reaches the last slice, with `--removeramps` added. On this map the correction changes only the last bits; the metrics table says where it matters more. The clean room's `fix` gives the replica's `fix` bit for bit, and its `reproduce` FSL's bytes.

{{ ev.example('fsl-prelude', 'ramps') }}

## A phase whose truth is known {#truth}

On a synthetic phase the truth is known. The record's case `opt/default` holds a smooth phase spanning several cycles, with noise, wrapped into [−π, π), and a magnitude from which prelude makes its own mask. FSL's unwrapped phase, the replica's and the clean room's are the true phase inside the mask, every wrap undone.

{{ ev.example('fsl-prelude', 'truth') }}

## Random testing {#random}

The replica's random-testing run (2026-11-06), 30 minutes long, drew random calls. Each was run by FSL 6.0.7.23 (through the cache of the original's runs) and by the replica, every file was compared, and the default, `fix`, was checked to name a correction exactly where it changes the result.

{{ ev.table('fsl-prelude', 'trial') }}

The clean room's random-testing run (2026-11-06), also 30 minutes long, drew 23,780 random calls. Each was run by FSL 6.0.7.23 (through the cache of the original's runs) and by the clean room: its `reproduce` compared with FSL's files and its `fix` with the replica's, as the record compares.

- 22,109 agreed.
- 14 more named GLIBC-07 where the correctly rounded arctangent and glibc's `atan2f` differ on a voxel of a complex image, whether or not an output changes, as the specification says.
- Each of the 1,657 that differed was run again with the part's final build and put in one category below. 1,650 were the clean room's own mistake, fixed with a permanent case of the record ([`difftest/time-step-zero-series`](#case=difftest/time-step-zero-series)): a series whose time step is 0 or negative, which FSL reads as its magnitude (and as 1 for a time step of 0), and which every output keeps.
- 7 stay open, each a question for the specification with its reproducer. On 6 oblique inputs whose offset is 0, FSL writes a residual of its own matrix arithmetic (1.8 × 10<sup>−15</sup> to 3.6 × 10<sup>−15</sup>) where the clean room writes 0, every other header field and every value the same. On 1, FSL-271 reproduced in the slices mode with a magnitude of more slices and fewer rows than the phase, FSL's mask at the phase's indices differs from the clean room's in one voxel (`fix` refuses the call in both ports).

{{ ev.table('fsl-prelude', 'trial-original') }}

{{ ev.table('fsl-prelude', 'trial-original-triage') }}

## Every case {#cases}

Each case of the two records, the replica's and the clean room's, both against FSL 6.0.7.23 (a column each), with what it tests, its command line, each port's verdict and the reason. The 78 cases only the clean room's record holds are its own: `orig-` and the permanent case random testing gave it. Search, filter by category or verdict (or select a segment of a chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('fsl-prelude') }}

## Speed {#speed}

FSL's prelude runs on one thread and spends its time in the merging, which scans every boundary sum for each choice: 6.7 s for fMRIPrep's call on ds005454 (14,678 regions) and 28.4 s on ds002603.

- The clean room takes 0.069 s and 0.135 s on one thread, 97 and 211 times FSL's speed and 2.5 and 2.8 times the replica's; 0.053 s and 0.103 s on 12.
- On a generated 128³ map of 66,020 regions it takes 0.30 s against FSL's 184 s (610 times), with 59 MiB against FSL's 64 MiB.
- On a 256 × 256 × 160 map of 152,738 regions it takes 2.0 s, where the replica takes 9.4 s and 469 MiB.
- On fMRIPrep's small calls every program's time is mostly its start and its reading and writing.

These timings come from [the report](repo:docs/benchmarks/fsl-prelude.md): the best of five runs of each call, FSL once, on a machine shared with other work. Every output was checked bit for bit.

{{ ev.speed('fsl-prelude') }}

{{ ev.table('fsl-prelude', 'benchmark') }}

## Corrections by default {#corrections}

Both ports correct FSL's deterministic defects by default, `fix`, and warn. The clean room names the same entries as the replica, and its `fix` is the replica's bit for bit but for GLIBC-07 (below). `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives FSL's behaviour byte for byte, where FSL's behaviour is defined ([register](repo:docs/findings/upstream-defects.md)).

- The ramps are taken over every column, row and slice (FSL-261, [above](#ramps)).
- With several volumes, `--savemask` and `-l` write one series of every volume's masks and labels (FSL-262: FSL writes each volume's to the same file in turn, so only the last is kept).
- `-c` with an image that is not complex is refused (FSL-263: FSL reads its bytes as complex values, past the buffer for 16-bit data).
- A big-endian complex image has each value's two parts swapped on their own (FSL-264: FSL swaps the eight bytes as one, so the real and imaginary parts change places).
- A complex128 image is read as such (FSL-265: FSL reads it with no width, from memory past an empty buffer).
- `-v` with ramps writes no `grot` file into the working directory (FSL-266).
- NaN magnitudes stay out of the threshold's percentiles and the maximum (FSL-268: in FSL a NaN first voxel empties the mask). NaN phases inside the mask stay out of it and come back as NaN in the output (FSL-269: in FSL a region labelled with a NaN voxel moves by about 2<sup>31</sup> cycles).
- `--end` before `--start`, which FSL accepts without writing anything (exit status 0), is refused with a reason (FSL-270); so is a magnitude or mask of another size than the phase, which FSL reads by the phase's indices (FSL-271).
- The phase's extrema are taken over its numbers (FSL-272, [above](#fsl272)).
- FSL's two messages that say otherwise than it does (the range allowed, "Removed linear ramps" printed twice) are kept as FSL prints them (FSL-267).

The clean room computes a complex image's phase with the correctly rounded arctangent on every platform by default. glibc's `atan2f` (FSL's build, and the replica's) is now and then one unit in the last place from the exact value rounded once. The clean room's `reproduce` computes it as glibc 2.35 does, and its `fix` names GLIBC-07 wherever the two differ on a voxel: the unwrapped phase keeps FSL's whole cycles, and a few phases differ in their last bit.

## Known limits {#limits}

Both ports are experimental. Each record's standard comparison holds fMRIPrep's calls on four fMRIPrep runs and the data panel's two other phase-difference maps. The full comparisons and the long random-testing runs come in the final validation phase.

Where FSL's result comes from memory it does not own (a NaN in the sorts of FSL-268 and FSL-269 that reaches outside the values, FSL-263's and FSL-265's complex values), both ports refuse in `reproduce` or fill the values deterministically, with a notice. The records then compare the exit status, the messages and the file names only.

The clean room's random-testing run left two questions for its specification ([above](#random)): FSL's residual in the offsets it writes back for an oblique image, and FSL-271's reading in the slices mode.

The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output.

## History {#history}

- **2026-11-06**: the replica, translated from FSL 6.0.7.23's source, with every option, message and failure case; twelve defects of FSL found (FSL-261 to FSL-272), eleven of them corrected by default or refused. Its random-testing run, 50,711 calls in 30 minutes.
- **2026-11-07**: the clean room, written from [specs/prelude.md](repo:specs/prelude.md), Jenkinson's paper, FSL's usage text and runs of FSL, and its random-testing run, 23,780 calls in 30 minutes; the permanent case `difftest/time-step-zero-series` from its triage.
- **2026-11-11**: the clean room's record made again: every case as before but `orig-types/unset` (14 of 14 checks, FSL-11 now named), and the files of its own cases in `fix` 252 of 252 the replica's bit for bit (248 of 248 before).
