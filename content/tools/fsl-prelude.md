---
title: prelude
kicker: Tools · FSL
lede: >-
  FSL's phase unwrapping (PRELUDE, Jenkinson 2003): a phase image is known only up to whole
  cycles of 2π, and prelude finds the cycles, region by region, that make it vary smoothly; it is
  the unwrapping fMRIPrep runs for every phase-difference field map. A clean-room original in
  LARMORX itself (Apache-2.0), experimental, written without FSL's code: every file prelude
  writes, its messages and its exit status bit for bit in every compared case of its record,
  fMRIPrep's seven calls included, and its default bit for bit the replica's; 97 and 211 times
  FSL's speed on fMRIPrep's two large calls on one thread, 610 times on a large generated map.
  And an exact replica of FSL 6.0.7.23's source in the separate larmorx-nc package (the FSL
  Licence's non-commercial terms), experimental, which gives every file prelude writes, its
  messages and its exit status bit for bit in every compared case of its record, fMRIPrep's
  seven calls included.
description: LARMORX's FSL prelude, a clean-room original and an exact replica validated against FSL 6.0.7.23 — fMRIPrep's seven phase-unwrapping calls on four oracle runs with fMRIPrep's own outputs, two corrections by default on real phase maps (a NaN first value, the ramps' last slice), a synthetic phase whose truth is known, both implementations' random testing with the original's triage, every parity case of both records with its verdict, and the speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>clean-room original (<code>larmorx</code>, Apache-2.0, crate <code>larmorx-fsl</code>), written from <a href="{{ repo('specs/prelude.md') }}">specs/prelude.md</a>, Jenkinson's paper, FSL's usage text and black-box runs of FSL 6.0.7.23 (2026-11-06 and 07); exact replica (<code>larmorx-nc</code>, under the FSL Licence's terms, run as a separate program), translated from FSL 6.0.7.23's source (fsl-fugue 2603.0, with newimage's complex reader)</dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span> (original) · <span class="status-tag status-tag--experimental">experimental</span> (replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/fsl-prelude.md') }}">fsl-prelude</a> (original, standard tier, FSL 6.0.7.23) · <a href="{{ repo('docs/validation/fsl-prelude-replica.md') }}">fsl-prelude-replica</a> (standard tier, FSL 6.0.7.23) · benchmark <a href="{{ repo('docs/benchmarks/fsl-prelude.md') }}">fsl-prelude</a> · API <a href="{{ repo('docs/api/fsl-prelude.md') }}">fsl-prelude</a></dd>
</dl>

## What it is

A gradient-echo field map measures the off-resonance field as a phase: the phase difference between two echoes is proportional to the field, but the scanner stores it only modulo 2π, so wherever the field is strong the stored phase jumps by a whole cycle between neighbouring voxels. Unwrapping adds back the missing cycles. prelude (*Phase Region Expanding Labeller for Unwrapping Discrete Estimates*; M. Jenkinson, Fast, automated, N-dimensional phase-unwrapping algorithm, Magnetic Resonance in Medicine 49:193–197, 2003) splits the phase range into `-n` intervals (8 by default), labels the connected regions of voxels whose phase falls in the same interval inside a mask, and then merges the regions two at a time: for each pair of touching regions it sums the phase differences across their boundary, from which follow the whole number of cycles that best joins them and how well it does (a measure that grows with the boundary's size and with how close the joining is to a whole number of cycles); the pair with the largest measure is merged first, the voxels of one region moved by that number of cycles, and the merged region's boundaries with its other neighbours are summed again. When one region remains, every voxel holds its phase plus its region's whole cycles. The mask is the given one (`-m`) or the magnitude's voxels above a threshold (`-t`, or by default a tenth of the way from the 2nd to the 98th percentile), kept to its largest connected part. The labels are 3D, or 2D slice by slice for images wider than 64 voxels (or with `--labelslices`); `-s` unwraps each slice on its own and joins the slices after; `--removeramps` removes the phase's linear ramp along each axis before unwrapping and restores it after. Its input is a phase and a magnitude (`-p`, `-a`), or a complex image (`-c`); a phase from 0 to 2π is rewrapped to [−π, π] first, and a phase spanning more than 3π is refused. Besides the unwrapped phase it writes, on request, the mask (`--savemask`), the regions' labels (`-l`) and the phase as read (`-r`).

fMRIPrep calls prelude for every phase-difference field map, in sdcflows' phase-difference workflow (`fmap_preproc_wf/<estimator>/phdiff_wf/prelude`): sdcflows first rescales the scanner's phase difference to radians from its minimum and maximum (or subtracts two phase images, each rescaled), clips the magnitude and extracts the brain, then runs `prelude --abs=<magnitude> --mask=<brain mask> --phase=<phase difference in rad> --unwrap=<out>` and turns the unwrapped phase into the field in Hz (divided by 2π and the echo-time difference).

```bash
larmorx fsl prelude --abs=magnitude --mask=brainmask --phase=phasediff_rad --unwrap=unwrapped
larmorx fsl prelude -c complex -o unwrapped --savemask=mask -l labels --removeramps -v
```

```python
import larmorx as lx

res = lx.fsl.prelude("phasediff_rad.nii.gz", "magnitude.nii.gz", mask="mask.nii.gz")
res.unwrapped            # lx.Image, float32, radians
res = lx.fsl.prelude(complex_image="complex.nii.gz", remove_ramps=True,
                     save_mask=True, save_labels=True)
res.mask, res.labels
```

FSL is distributed under the FSL Licence, which allows non-commercial use only, so LARMORX keeps its FSL tools in two implementations: the exact replica translated from FSL's source, in the separate package `larmorx-nc` (`pip install larmorx-nc`), and a clean-room original in LARMORX itself, written from a behavioural specification without FSL's code. `implementation="auto"` (and `larmorx fsl prelude`) runs the replica when `larmorx-nc` is installed and the clean-room original otherwise; `implementation="original"` (on the command line `LARMORX_IMPLEMENTATION=original`) chooses the original. The clean-room original is written from prelude's behavioural specification ([specs/prelude.md](repo:specs/prelude.md)), Jenkinson's paper, FSL's usage text and black-box runs of FSL 6.0.7.23, never from FSL's code: every option, message, exit status and failure case, the defects with their switches, every file prelude writes bit for bit (the specification's threshold). It is built for speed: where FSL looks for the next merge by scanning every constraint, for the members of the region that joins by scanning every region, and for its neighbours by scanning every region number, the original keeps the constraints in slots reused by the merges, an indexed heap of the candidate merges keyed by their merit and pair, each region's list of constraints and a weighted union-find of the regions' whole cycles, so a choice costs a logarithm and a merge the neighbours of the region that joins; it makes FSL's choices in FSL's order with FSL's arithmetic, so the bits are FSL's. The linear parts (the mask's threshold and its component, the regions, the ramps, reading and writing) run on the call's threads in fixed chunks, so the result is the same bits at any thread count; it holds no copy of the phase where none is needed. The replica follows FSL 6.0.7.23, runs none of FSL's programs and needs no FSL installation; it keeps FSL's merging order exactly (the same constraints, the same arithmetic in the same order), with a faster bookkeeping of the regions and their boundaries (ordered sets). How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

The clean-room original is written without FSL's code, so the question for it is whether it gives FSL's result within the threshold of [specs/prelude.md](repo:specs/prelude.md) §11: every file prelude writes bit for bit (each image's header, its extension bytes included, but `descrip`, and its data), FSL's standard output and error and its exit status, the same in its reproduce mode, and its default mode the replica's default; each case's verdict is read from what the record measures.

{{ ev.agreement('fsl-prelude', 'original') }}

The original's record runs 166 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-prelude.md)): the replica suite's 88 cases, with the original standing in for the replica's program and FSL's runs from the oracle cache, its own 77 (`orig-`: the specification's validation plan on generated inputs, every option, image type, orientation, series, complex image, NaN, output type and failure, and fMRIPrep's seven calls run three ways) and a permanent case of random testing. 134 give FSL's files byte for byte, with FSL's messages and exit status (fMRIPrep's seven calls among them, each also against fMRIPrep's own output); in 28 FSL refuses the input or stops and the original does the same (*rejected by both*); in 4 FSL reads values from memory it never wrote (a complex128 image, FSL-265, twice; an image that is not complex given to `-c`, FSL-263, twice): the exit status, messages and file names are FSL's and the values are not compared (*expected divergence*). In its reproduce mode 282 of 282 files of its own cases are FSL's headers and data bit for bit; by default 248 of 248 are the replica's default bit for bit, and on the 5 complex images whose phase it computes with the correctly rounded arctangent (GLIBC-07, [below](#corrections)) the unwrapped phase keeps the replica's whole cycles on every voxel of the mask.

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes: every file prelude writes (each image's header and data: the unwrapped phase, the mask, the labels, the raw phase), its standard output and error, and its exit status.

{{ ev.agreement('fsl-prelude', 'replica') }}

The record runs 88 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-prelude-replica.md)): 67 give FSL's files byte for byte, in 20 FSL refuses the input or stops and the replica does the same, with the same message and exit status (*rejected by both*), and in one FSL reads a complex128 image with no width, so its values come from memory it never wrote (FSL-265: *expected divergence*, the exit status, messages and file names compared). They cover fMRIPrep's seven calls on its four oracle runs (fMRIPrep's own outputs the same too), the data panel's two other phase-difference maps, every option (phase and magnitude or complex input in both byte orders and widths, the mask and its threshold, 3D and 2D labels and unwrapping, the phase intervals, series with `--start` and `--end`, the saved mask, labels and raw phase, the ramps, `-v`'s messages), every output type, NaN values in the magnitude and the phase, and every message, exit status and failure case of the command line. Each case also runs the replica's default mode, where LARMORX corrects FSL's deterministic defects and names them (below).

## In fMRIPrep: the phase differences of four oracle runs {#fmriprep}

fMRIPrep's seven prelude calls, each given to FSL 6.0.7.23 (the record's run, served from the oracle-output cache), to the replica in its reproduce and default modes and to the clean-room original in its reproduce mode at 14 threads and at one and in its default mode, with fMRIPrep's own output beside them (prelude in fMRIPrep's image). Every comparison gives the same bytes; the first table counts what unwrapping did in each, the second gives the original's comparisons and the benchmark's seconds.

{{ ev.table('fsl-prelude', 'fmriprep-calls') }}

{{ ev.table('fsl-prelude', 'fmriprep-calls-original') }}

### ds005454: a GRE phase difference {#ds005454}

The input panels are what prelude is given: the phase difference wrapped into 0 to 2π, the magnitude and the brain mask (drawn over the magnitude). The viewer opens where unwrapping added the most cycles in its slice; the replica's and the clean-room original's differences from FSL and from fMRIPrep's own output are zero everywhere, at 14 threads and at one.

{{ ev.example('fsl-prelude', 'fmriprep-ds005454') }}

### ds002603: a Philips phase difference at 2 mm {#ds002603}

{{ ev.example('fsl-prelude', 'fmriprep-ds002603') }}

### ds002422: two phase differences at 1.5 T {#ds002422}

The data panel's 1.5 T subject has two phase-difference maps, on different grids, each unwrapped by its own call.

{{ ev.example('fsl-prelude', 'fmriprep-ds002422-run01') }}

{{ ev.example('fsl-prelude', 'fmriprep-ds002422-run02') }}

### ds001600: three field-map protocols {#ds001600}

ds001600 holds several field-map protocols of one subject: two of them store two phase images, which sdcflows subtracts before prelude (`acq-v1`, `acq-v2`), and one a phase difference (`acq-v4`).

{{ ev.example('fsl-prelude', 'fmriprep-ds001600-v1') }}

{{ ev.example('fsl-prelude', 'fmriprep-ds001600-v2') }}

{{ ev.example('fsl-prelude', 'fmriprep-ds001600-v4') }}

## A NaN first value, and a correction by default {#fsl272}

FSL takes the phase's maximum and minimum from its first value on, so a phase map whose first value is NaN (the first voxel of a masked or divided map) gets a NaN maximum and minimum: the range check and the rewrap to [−π, π] are both skipped (FSL-272). A phase from 0 to 2π is then unwrapped in other intervals, and some regions come out whole cycles wrong relative to the rest. Measured before deciding (rule D: fMRIPrep's seven maps and a synthetic one, each moved to [0, 2π) with its first value NaN): seven of the eight came out whole cycles wrong in some regions. The replica's default takes the extrema over the values that are numbers, which gives what FSL gives for the same map without the NaN; its reproduce mode gives FSL's bytes. Below, ds002603's map so changed: compare *FSL with the NaN − FSL without it* (the defect) with *replica (default) − FSL without the NaN* (the correction). The clean-room original does the same: its reproduce mode gives FSL's bytes with the NaN, and its default FSL's result without it (*clean-room original (default) − FSL without the NaN*, zero everywhere).

{{ ev.example('fsl-prelude', 'fsl272') }}

## The ramps' last slice, and a correction by default {#ramps}

With `--removeramps` FSL's loops stop one column, row and slice short, so the last slice is unwrapped with its ramp while the rest is unwrapped without it, and an image of one slice gets no ramp removed at all (FSL-261). The replica's default takes every column, row and slice. fMRIPrep does not ask for the ramps' removal; below, its call on ds002422's second map, whose brain mask reaches the last slice, with `--removeramps` added. On this map the correction changes only the last bits; the metrics table says where it matters more. The clean-room original's default gives the replica's default bit for bit, and its reproduce mode FSL's bytes.

{{ ev.example('fsl-prelude', 'ramps') }}

## A phase whose truth is known {#truth}

On a synthetic phase the truth is known: the record's case `opt/default`, a smooth phase spanning several cycles, with noise, wrapped into [−π, π), and a magnitude from which prelude makes its own mask. FSL's unwrapped phase, the replica's and the clean-room original's are the true phase inside the mask, every wrap undone.

{{ ev.example('fsl-prelude', 'truth') }}

## Random testing {#random}

Differential random testing's trial of this part: half an hour of random calls, each run by FSL 6.0.7.23 (through the oracle cache) and by the replica, every file compared and the default mode checked by D13's rule.

{{ ev.table('fsl-prelude', 'trial') }}

The clean-room original's trial: half an hour of random calls (23,780), each run by FSL 6.0.7.23 (through the oracle cache) and by the original, its reproduce mode compared with FSL's files and its default with the replica's, as the record compares. 22,109 agreed, and 14 more named GLIBC-07 where the correctly rounded arctangent and glibc's `atan2f` differ on a voxel of a complex image, whether or not an output changes (as the specification says). Each of the 1,657 that differed was run again with the part's final build and put in one category below: 1,650 were the original's own mistake, fixed with a permanent case of the record ([`difftest/time-step-zero-series`](#case=difftest/time-step-zero-series)): a series whose time step is 0 or negative, which FSL reads as its magnitude (and as 1 for a time step of 0) and every output keeps. 7 stay open, each a question for the specification with its reproducer: on 6 oblique inputs whose offset is 0 FSL writes a residual of its own matrix arithmetic (1.8 × 10<sup>−15</sup> to 3.6 × 10<sup>−15</sup>) where the original writes 0, every other header field and every value the same; on 1, FSL-271 reproduced in the slices mode with a magnitude of more slices and fewer rows than the phase, FSL's mask at the phase's indices differs from the original's in one voxel (the default refuses the call in both).

{{ ev.table('fsl-prelude', 'trial-original') }}

{{ ev.table('fsl-prelude', 'trial-original-triage') }}

## Every case {#cases}

Each case of both records, with what it tests, its command line, each implementation's verdict and the reason (the 78 cases only the clean-room original's record holds are its own: `orig-` and the permanent case random testing gave it). Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('fsl-prelude') }}

## Speed {#speed}

FSL's prelude runs on one thread and spends its time in the merging, which scans every constraint for each choice: 6.7 s for fMRIPrep's call on ds005454 (14,678 regions) and 28.4 s on ds002603. The clean-room original takes 0.069 s and 0.135 s on one thread (97 and 211 times FSL's speed, 2.5 and 2.8 times the replica's), 0.053 s and 0.103 s on 12; on a generated 128³ map of 66,020 regions 0.30 s against FSL's 184 s (610 times), with 59 MiB against FSL's 64 MiB; on a 256 × 256 × 160 map of 152,738 regions 2.0 s, where the replica takes 9.4 s and 469 MiB. On fMRIPrep's small calls every program's time is mostly its start and its reading and writing ([the report](repo:docs/benchmarks/fsl-prelude.md): the best of five runs of each call, FSL once, on a machine shared with another agent's work; every output checked bit for bit).

{{ ev.speed('fsl-prelude') }}

{{ ev.table('fsl-prelude', 'benchmark') }}

## Corrections by default {#corrections}

Both implementations correct FSL's deterministic defects by default and warn (the clean-room original names the same entries as the replica, its default the replica's bit for bit but for GLIBC-07, below), with `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) giving FSL's behaviour byte for byte where FSL's is defined ([register](repo:docs/findings/upstream-defects.md)). The ramps over every column, row and slice (FSL-261, above). With several volumes, `--savemask` and `-l` write one series of every volume's masks and labels (FSL-262: FSL writes each volume's to the same file in turn, so only the last is kept). `-c` with an image that is not complex is refused (FSL-263: FSL reads its bytes as complex values, past the buffer for 16-bit data). A big-endian complex image has each value's two parts swapped on their own (FSL-264: FSL swaps the eight bytes as one, so the real and imaginary parts change places). A complex128 image is read as such (FSL-265: FSL reads it with no width, from memory past an empty buffer). `-v` with ramps writes no `grot` file into the working directory (FSL-266). NaN magnitudes stay out of the threshold's percentiles and the maximum (FSL-268: in FSL a NaN first voxel empties the mask), and NaN phases inside the mask stay out of it and come back as NaN in the output (FSL-269: in FSL a region labelled with a NaN voxel moves by about 2<sup>31</sup> cycles). `--end` before `--start`, which FSL accepts without writing anything (exit status 0), and a magnitude or mask of another size than the phase, which FSL reads by the phase's indices, are refused with a reason (FSL-270, FSL-271). The phase's extrema over its numbers (FSL-272, above). FSL's two messages that say otherwise than it does (the range allowed, "Removed linear ramps" printed twice) are kept as FSL prints them (FSL-267). The clean-room original computes a complex image's phase with the correctly rounded arctangent on every platform by default, where glibc's `atan2f` (FSL's build, and the replica's) is now and then one unit in the last place from the exact value rounded once; its reproduce mode computes it as glibc 2.35 does, and its default names GLIBC-07 wherever the two differ on a voxel: the unwrapped phase keeps FSL's whole cycles, and a few phases differ in their last bit.

## Known limits {#limits}

Both implementations are experimental. Their records' standard tier holds fMRIPrep's calls on its four oracle runs and the data panel's two other phase-difference maps; the full tiers and long random testing run in the final validation phase. Where FSL's result comes from memory it does not own (a NaN in the sorts of FSL-268 and FSL-269 that reaches outside the values, FSL-263's and FSL-265's complex values), both refuse in reproduce mode or fill the values deterministically, with a notice, and the records compare the exit status, the messages and the file names only. The clean-room original's trial left two questions for the specification (above): FSL's residual in the offsets it writes back for an oblique image, and FSL-271's reading in the slices mode. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md).
