---
title: prelude
kicker: Tools · FSL
lede: >-
  FSL's phase unwrapping (PRELUDE, Jenkinson 2003): a phase image is known only up to whole
  cycles of 2π, and prelude finds the cycles, region by region, that make it vary smoothly; it is
  the unwrapping fMRIPrep runs for every phase-difference field map. An exact replica of FSL
  6.0.7.23's source in the separate larmorx-nc package (the FSL Licence's non-commercial terms),
  experimental, which gives every file prelude writes, its messages and its exit status bit for
  bit in every compared case of its record, fMRIPrep's seven calls included. The clean-room
  original is the next part.
description: LARMORX's FSL prelude, an exact replica validated against FSL 6.0.7.23 — fMRIPrep's seven phase-unwrapping calls on four oracle runs with fMRIPrep's own outputs, two corrections by default on real phase maps (a NaN first value, the ramps' last slice), a synthetic phase whose truth is known, random testing's trial, and every parity case of the record with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-nc</code>, under the FSL Licence's terms, run as a separate program), translated from FSL 6.0.7.23's source (fsl-fugue 2603.0, with newimage's complex reader); clean-room original (<code>larmorx</code>, Apache-2.0): the next part, to be written from <a href="{{ repo('specs/prelude.md') }}">specs/prelude.md</a></dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span> (replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/fsl-prelude-replica.md') }}">fsl-prelude-replica</a> (standard tier, FSL 6.0.7.23) · API <a href="{{ repo('docs/api/fsl-prelude.md') }}">fsl-prelude</a></dd>
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

FSL is distributed under the FSL Licence, which allows non-commercial use only, so LARMORX keeps its FSL tools in two implementations: the exact replica translated from FSL's source, in the separate package `larmorx-nc` (`pip install larmorx-nc`), and a clean-room original in LARMORX itself, written from a behavioural specification without FSL's code. For prelude only the replica exists so far: `implementation="auto"` (and `larmorx fsl prelude`) runs it when `larmorx-nc` is installed, and a clear error names the package otherwise. The replica follows FSL 6.0.7.23, runs none of FSL's programs and needs no FSL installation; it keeps FSL's merging order exactly (the same constraints, the same arithmetic in the same order), with a faster bookkeeping of the regions and their boundaries. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes: every file prelude writes (each image's header and data: the unwrapped phase, the mask, the labels, the raw phase), its standard output and error, and its exit status.

{{ ev.agreement('fsl-prelude', 'replica') }}

The record runs 88 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-prelude-replica.md)): 67 give FSL's files byte for byte, in 20 FSL refuses the input or stops and the replica does the same, with the same message and exit status (*rejected by both*), and in one FSL reads a complex128 image with no width, so its values come from memory it never wrote (FSL-265: *expected divergence*, the exit status, messages and file names compared). They cover fMRIPrep's seven calls on its four oracle runs (fMRIPrep's own outputs the same too), the data panel's two other phase-difference maps, every option (phase and magnitude or complex input in both byte orders and widths, the mask and its threshold, 3D and 2D labels and unwrapping, the phase intervals, series with `--start` and `--end`, the saved mask, labels and raw phase, the ramps, `-v`'s messages), every output type, NaN values in the magnitude and the phase, and every message, exit status and failure case of the command line. Each case also runs the replica's default mode, where LARMORX corrects FSL's deterministic defects and names them (below).

## In fMRIPrep: the phase differences of four oracle runs {#fmriprep}

fMRIPrep's seven prelude calls, each given to FSL 6.0.7.23 (the record's run, served from the oracle-output cache) and to the replica in its reproduce and default modes, with fMRIPrep's own output beside them (prelude in fMRIPrep's image). Every comparison gives the same bytes; the table counts what unwrapping did in each.

{{ ev.table('fsl-prelude', 'fmriprep-calls') }}

### ds005454: a GRE phase difference {#ds005454}

The input panels are what prelude is given: the phase difference wrapped into 0 to 2π, the magnitude and the brain mask (drawn over the magnitude). The viewer opens where unwrapping added the most cycles in its slice; the replica's differences from FSL and from fMRIPrep's own output are zero everywhere.

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

FSL takes the phase's maximum and minimum from its first value on, so a phase map whose first value is NaN (the first voxel of a masked or divided map) gets a NaN maximum and minimum: the range check and the rewrap to [−π, π] are both skipped (FSL-272). A phase from 0 to 2π is then unwrapped in other intervals, and some regions come out whole cycles wrong relative to the rest. Measured before deciding (rule D: fMRIPrep's seven maps and a synthetic one, each moved to [0, 2π) with its first value NaN): seven of the eight came out whole cycles wrong in some regions. The replica's default takes the extrema over the values that are numbers, which gives what FSL gives for the same map without the NaN; its reproduce mode gives FSL's bytes. Below, ds002603's map so changed: compare *FSL with the NaN − FSL without it* (the defect) with *replica (default) − FSL without the NaN* (the correction).

{{ ev.example('fsl-prelude', 'fsl272') }}

## The ramps' last slice, and a correction by default {#ramps}

With `--removeramps` FSL's loops stop one column, row and slice short, so the last slice is unwrapped with its ramp while the rest is unwrapped without it, and an image of one slice gets no ramp removed at all (FSL-261). The replica's default takes every column, row and slice. fMRIPrep does not ask for the ramps' removal; below, its call on ds002422's second map, whose brain mask reaches the last slice, with `--removeramps` added. On this map the correction changes only the last bits; the metrics table says where it matters more.

{{ ev.example('fsl-prelude', 'ramps') }}

## A phase whose truth is known {#truth}

On a synthetic phase the truth is known: the record's case `opt/default`, a smooth phase spanning several cycles, with noise, wrapped into [−π, π), and a magnitude from which prelude makes its own mask. FSL's unwrapped phase and the replica's are the true phase inside the mask, every wrap undone.

{{ ev.example('fsl-prelude', 'truth') }}

## Random testing {#random}

Differential random testing's trial of this part: half an hour of random calls, each run by FSL 6.0.7.23 (through the oracle cache) and by the replica, every file compared and the default mode checked by D13's rule.

{{ ev.table('fsl-prelude', 'trial') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, its verdict and the reason. Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('fsl-prelude') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default and warns, with `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) giving FSL's behaviour byte for byte where FSL's is defined ([register](repo:docs/findings/upstream-defects.md)). The ramps over every column, row and slice (FSL-261, above). With several volumes, `--savemask` and `-l` write one series of every volume's masks and labels (FSL-262: FSL writes each volume's to the same file in turn, so only the last is kept). `-c` with an image that is not complex is refused (FSL-263: FSL reads its bytes as complex values, past the buffer for 16-bit data). A big-endian complex image has each value's two parts swapped on their own (FSL-264: FSL swaps the eight bytes as one, so the real and imaginary parts change places). A complex128 image is read as such (FSL-265: FSL reads it with no width, from memory past an empty buffer). `-v` with ramps writes no `grot` file into the working directory (FSL-266). NaN magnitudes stay out of the threshold's percentiles and the maximum (FSL-268: in FSL a NaN first voxel empties the mask), and NaN phases inside the mask stay out of it and come back as NaN in the output (FSL-269: in FSL a region labelled with a NaN voxel moves by about 2<sup>31</sup> cycles). `--end` before `--start`, which FSL accepts without writing anything (exit status 0), and a magnitude or mask of another size than the phase, which FSL reads by the phase's indices, are refused with a reason (FSL-270, FSL-271). The phase's extrema over its numbers (FSL-272, above). FSL's two messages that say otherwise than it does (the range allowed, "Removed linear ramps" printed twice) are kept as FSL prints them (FSL-267).

## Known limits {#limits}

The replica is experimental. The record's standard tier holds fMRIPrep's calls on its four oracle runs and the data panel's two other phase-difference maps; its full tier and long random testing run in the final validation phase. Where FSL's result comes from memory it does not own (a NaN in the sorts of FSL-268 and FSL-269 that reaches outside the values, FSL-265's complex128 values), the replica refuses in reproduce mode or fills the values deterministically, with a notice. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). There is no benchmark report yet: speed is to be measured with the clean-room original.
