---
title: fslstats
kicker: Tools · FSL
lede: >-
  FSL's image statistics: the mean, standard deviation, extremes, robust range, percentiles,
  entropy, voxel count and volume, centre of gravity, bounding box or histogram of an image, its
  options applied in order (thresholds, masks, absolute values and a difference image change what
  the later options see), per volume, per label or as JSON. fMRIPrep's goodvoxels mask reads four
  of its numbers, and BET's script one. A clean-room original in LARMORX itself (Apache-2.0),
  experimental, written without FSL's code, which prints FSL's numbers in 125 of its record's
  126 compared cases, fMRIPrep's goodvoxels calls included, and BET's call within the record's
  bound (6 × 10⁻⁸ relative); 36 more rejected by both alike. And an exact replica of FSL
  6.0.7.23's source in the separate larmorx-nc package (the FSL Licence's non-commercial terms),
  experimental, which prints FSL's text byte for byte, with its messages and exit status, in
  every compared case of its record.
description: LARMORX's fslstats, a clean-room original and an exact replica validated against FSL 6.0.7.23 — fMRIPrep's goodvoxels calls and BET's call, every option on a real image with -t, -K and -json, FSL's own tests (the replica), both implementations' random testing with the original's triage, every parity case of both records with its verdict, and the speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>clean-room original (<code>larmorx</code>, Apache-2.0, crate <code>larmorx-fsl</code>), written from <a href="{{ repo('specs/fslstats.md') }}">specs/fslstats.md</a>, FSL's usage text and documentation and black-box runs of FSL 6.0.7.23 (2026-11-03); exact replica (<code>larmorx-nc</code>, under the FSL Licence's terms, run as a separate program), translated from FSL 6.0.7.23's source (fsl-avwutils 2209.6, with fsl-newimage 2601.0's statistics and nlohmann/json 3.12.0's number formatting)</dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span> (original) · <span class="status-tag status-tag--experimental">experimental</span> (replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/fsl-stats.md') }}">fsl-stats</a> (original, standard tier, FSL 6.0.7.23) · <a href="{{ repo('docs/validation/fsl-stats-replica.md') }}">fsl-stats-replica</a> (standard tier, FSL 6.0.7.23) · benchmark <a href="{{ repo('docs/benchmarks/fsl-maths.md') }}">fsl-maths</a> (with fslmaths) · API <a href="{{ repo('docs/api/fsl-stats.md') }}">fsl-stats</a> · its companion: <a href="{{ link('/tools/fsl-maths/') }}">fslmaths</a></dd>
</dl>

## What it is

`fslstats [-t] [-K <labels>] [-json] <image> [options]` prints statistics of an image. The options act in their order: `-l` and `-u` set lower and upper thresholds, `-k` a mask, `-d` a difference image, `-a` takes absolute values and `-n` turns NaN into 0, each for the options after it; the others print a number or a few: `-m`, `-M` (the mean, of the nonzero voxels), `-s`, `-S` (the standard deviation), `-R` (minimum and maximum), `-r` (the robust range, 2 % and 98 %), `-p`, `-P` (percentiles), `-e`, `-E` (entropy), `-v`, `-V` (voxels and volume), `-w` (the smallest box holding the nonzero voxels), `-x`, `-X` (the maximum's and minimum's voxels), `-c`, `-C` (centre of gravity, in mm and voxels), `-h`, `-H` (histograms). `-t` prints one line per volume, `-K` one per label of an index image, `-json` everything as JSON. Numbers print with six decimals, as nipype reads them.

fMRIPrep reads four of them in its goodvoxels mask (`--project-goodvoxels`: `-M` and `-S` of the ribbon's coefficient of variation, before and after its modulation), and BET's script one (`fslstats <image> -l <t> -C`, its starting centre), which LARMORX's BET replica runs through this code.

```bash
larmorx fsl fslstats cov_ribbon.nii.gz -M -S
larmorx fsl fslstats -t -K labels.nii.gz bold.nii.gz -M
```

```python
import larmorx as lx

text = lx.fsl.fslstats("cov_ribbon.nii.gz", "-M", "-S")   # the command line's options: its standard output
mean = lx.fsl.image_mean("cov_ribbon.nii.gz", nonzero=True)  # one typed wrapper per statistic: numbers
```

FSL is distributed under the FSL Licence, which allows non-commercial use only, so LARMORX keeps its FSL tools in two implementations: the exact replica translated from FSL's source, in the separate package `larmorx-nc` (`pip install larmorx-nc`), and a clean-room original in LARMORX itself, written from a behavioural specification without FSL's code. `implementation="auto"` (and `larmorx fsl fslstats`) runs the replica when `larmorx-nc` is installed and the clean-room original otherwise; `implementation="original"` (on the command line `LARMORX_IMPLEMENTATION=original`) chooses the original. The clean-room original is written from fslstats' behavioural specification ([specs/fslstats.md](repo:specs/fslstats.md)), FSL's usage text and documentation and black-box runs of FSL 6.0.7.23, never from FSL's code: every option and preoption (`-t`, `-K`, `-json`), every message, exit status and failure case (a crash's lost buffered output included), the defects with their switches, nlohmann's number format for `-json` as the specification describes it. Its passes run in parallel, the masked sums in FSL's blocks added in order, so its text is the same at any thread count; it holds one copy of the image. Where the specification leaves a convention open it follows FSL's as black-box runs measured it (findings 21 and 28 of its [findings](repo:docs/findings/fsl-maths-original.md)). The replica follows FSL 6.0.7.23 and needs no FSL installation; it lives in `larmorx-nc`'s shared core, beside the image statistics FAST and BET use, with nlohmann/json 3.12.0's number formatting for `-json`. How to read what follows: [the validation guide](/validation/#reading).

**The C library's last digits (since 2026-11-04).** fslstats' entropies (`-e`, `-E`) take logarithms from glibc, the C library of Linux, whose results are now and then one unit in the last place from the exact value rounded once. LARMORX computes them correctly rounded, the same on every platform; since 2026-11-04 the clean-room original's `reproduce` mode computes them exactly as glibc 2.35 does, and its default correctly rounded, naming GLIBC-07 exactly where the printed number would differ ([register](repo:docs/findings/upstream-defects.md)). On every case of its record the printed numbers, to their six digits, are the same either way: no number of the record moved.

## The verdicts at a glance {#verdicts}

fslstats prints numbers. The clean-room original is held to [specs/fslstats.md](repo:specs/fslstats.md) §10: the counts, extremes, coordinates, the robust range, percentiles, histograms, `-w` and the masked means and standard deviations identical to FSL's, the other numbers (the unmasked means and standard deviations, `-D`, the entropies, the centres of gravity) within 10<sup>−6</sup> relative, its messages and exit status FSL's.

{{ ev.agreement('fsl-stats', 'original') }}

The original's record runs 162 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-stats.md)): the replica suite's cases but FSL's own tests (they read FSL's source tree, which a clean-room implementer does not open), BET's call, 9 of its own (`orig/`) and 4 permanent cases of random testing. 125 print FSL's numbers, with its messages and exit status, fMRIPrep's four goodvoxels calls among them; one, BET's `-l 0.001 -C` on fMRIPrep's preprocessed T1w, is within the bound: its x 97.862248 against FSL's 97.862242, 6.1 × 10<sup>−8</sup> relative (the mapping back to millimetres of a neurological image, whose arithmetic in FSL a black box does not show); 36 are rejected by both alike.

The question for the replica is whether it prints FSL's text, character for character, with FSL's messages and exit status.

{{ ev.agreement('fsl-stats', 'replica') }}

The record runs 208 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-stats-replica.md)): 172 print FSL's text byte for byte, and in 36 FSL refuses the input or stops and the replica does the same, with the same message and exit status (*rejected by both*). They cover fMRIPrep's four goodvoxels calls, BET's call on fMRIPrep's preprocessed T1w, FSL's own tests of fslstats (each option in text and in JSON, against FSL's expected outputs as well), every option in every data type and in combination, the options' order, `-t`, `-K` and `-json`, every message and failure case, and the defects LARMORX corrects by default: each case also runs the replica's default mode, which names every correction where it changes the output (below).

## In fMRIPrep: the goodvoxels mask {#goodvoxels}

The four numbers fMRIPrep's goodvoxels workflow reads between its fslmaths calls, on ds005040's BOLD series in T1w space ([the fourteen fslmaths calls](/tools/fsl-maths/#goodvoxels)): FSL 6.0.7.23's printed text, the replica's in both modes and the clean-room original's in both modes, each the same. fMRIPrep divides the coefficient-of-variation images by the two means and thresholds the modulated one at its mean plus half its standard deviation. The oracle runs have no FreeSurfer reconstruction, so the cortical ribbon is a stand-in, the segmentation's grey matter.

{{ ev.table('fsl-stats', 'goodvoxels') }}

## Every option on a real image {#options}

Each option once on real data, as a pipeline would call it: FSL's mean and standard deviation of ds005040's BOLD series in T1w space, the series itself (63 volumes) for `-t`, fMRIPrep's brain mask for `-k`, fMRIPrep's segmentation (grey matter, white matter, CSF) at each BOLD voxel for `-K`, and BET's call on fMRIPrep's preprocessed T1w. The replica prints FSL's text in every one. Its default mode differs where a correction applies: without a mask, FSL squares each value of `-S` in single precision, so its standard deviation of the nonzero voxels is 29842.182847 where `-s` gives 29842.182845 for the same voxels; the default takes the masked form and prints the latter (FSL-182, named). The clean-room original prints FSL's text in every one but BET's call (its centre of gravity within §10's bound, above), at 14 threads and at one; its default mode makes FSL-182's correction too, and names it.

{{ ev.table('fsl-stats', 'options') }}

## Random testing {#random}

Differential random testing's trial of this part (shared with fslmaths): random option lists on random images, each run by FSL 6.0.7.23 (through the oracle cache) and by the replica, the printed text compared.

{{ ev.table('fsl-stats', 'trial') }}

The clean-room original's trial (beside fslmaths', 20 minutes): 150,000 random option lists, the preoptions and fMRIPrep's and BET's forms among them, each compared as the record compares. 149,214 agreed and 7 differed only by a correction the default mode names. Of the 779 that differed, run again with the part's final build: 545 were the original's mistake, fixed with permanent cases (the histograms of `-h` and `-H` when no histogram is made), 74 the suite's (§10's bound over a histogram's lines and an output cut short), and 160 are explained: `-c` and `-C` of images holding NaN and infinities, where FSL's NaN carries another sign (129), and the last printed digit at §10's bound (31). None stays open.

{{ ev.table('fsl-stats', 'trial-original') }}

{{ ev.table('fsl-stats', 'trial-original-triage') }}

## Every case {#cases}

Each case of both records, with what it tests, its command line, each implementation's verdict and the reason (the 13 cases only the clean-room original's record holds are its own: `orig/` and the permanent cases random testing gave it). Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('fsl-stats') }}

## Speed {#speed}

Reading the image is most of fslstats' time. On BET's call on fMRIPrep's preprocessed T1w the clean-room original takes 0.45 s on one thread and 0.29 s on 14, against FSL's 0.58 s; on 63 volumes of a BOLD series (`-t -M -S -r`) 0.22 s against 0.23 s, with less memory than FSL (41 MiB against 47). The replica takes 0.34 and 0.23 s ([the report](repo:docs/benchmarks/fsl-maths.md), shared with fslmaths: informal, one run each, on a machine shared with another agent's work).

{{ ev.speed('fsl-stats') }}

{{ ev.table('fsl-stats', 'benchmark') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default and warns, with `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) giving FSL's output byte for byte where FSL's is defined ([register](repo:docs/findings/upstream-defects.md)); where FSL crashes, the replica refuses in both modes or gives a defined result. NaN values are left out of the order statistics: `-R`, `-x`, `-X`, the percentiles, the histograms and the robust range (FSL-181). Without a mask, `-s` and `-S` take the masked forms: the variance clamped at 0 and 0 for a single value, `-S`'s squares in double precision (FSL-182). With `-t`, a 4D `-k` or `-d` image gives each time point its volume (FSL-183). `-x` and `-X` of a mask without voxels are refused in both modes, where FSL crashes (FSL-184). `-e` and `-E` of an image whose robust range is empty give the entropy 0 instead of crashing (FSL-185). `-H` with a maximum not above its minimum is an error, where FSL prints nothing (FSL-186). A value more than about two billion bin widths above a histogram's range counts in its last bin (FSL-187: `-H`, `-e`, `-E`, `-r`; shared with fslmaths, BET and FLIRT). `-w` of a 4D image without nonzero voxels gives the whole time range (FSL-188). `-json` writes voxel counts exactly, where FSL rounds them to single precision above 16,777,216 (FSL-189). The clean-room original makes the same corrections by default with the same notices (FSL-181 to FSL-189), and its reproduce mode follows FSL where FSL's output is defined; where FSL crashes, its reproduce mode prints what FSL's buffer had written before the crash and ends with exit status 1.

## Known limits {#limits}

Both implementations are experimental. The clean-room original is held to §10's bound for the numbers FSL sums without a mask and for the centres of gravity (BET's call: 6 × 10<sup>−8</sup> relative); FSL's own tests of fslstats are not among its cases (they read FSL's source tree), and they may be run against it later, as a check outside the clean room. The replica's record's standard tier holds fMRIPrep's and BET's calls; its full tier, the data panel and long random testing run in the final validation phase. The goodvoxels calls use a stand-in for the cortical ribbon, to be checked again with a real ribbon once an fMRIPrep run with FreeSurfer's reconstruction exists. Images compressed with zstd or bzip2 are decompressed whole before they are read. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). The benchmark is informal: one run each, on a shared machine.
