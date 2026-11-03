---
title: fslstats
kicker: Tools · FSL
lede: >-
  FSL's image statistics: the mean, standard deviation, extremes, robust range, percentiles,
  entropy, voxel count and volume, centre of gravity, bounding box or histogram of an image, its
  options applied in order (thresholds, masks, absolute values and a difference image change what
  the later options see), per volume, per label or as JSON. fMRIPrep's goodvoxels mask reads four
  of its numbers, and BET's script one. An exact replica of FSL 6.0.7.23's source in the separate
  larmorx-nc package (the FSL Licence's non-commercial terms), experimental, which prints FSL's
  text byte for byte, with its messages and exit status, in every compared case of its record.
  The clean-room original is still to be written.
description: LARMORX's fslstats, an exact replica validated against FSL 6.0.7.23 — fMRIPrep's goodvoxels calls and BET's call, every option on a real image with -t, -K and -json, FSL's own tests, random testing's trial, and every parity case of the record with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-nc</code>, under the FSL Licence's terms, run as a separate program), translated from FSL 6.0.7.23's source (fsl-avwutils 2209.6, with fsl-newimage 2601.0's statistics and nlohmann/json 3.12.0's number formatting); clean-room original (<code>larmorx</code>, Apache-2.0): planned, to be written from <a href="{{ repo('specs/fslstats.md') }}">specs/fslstats.md</a></dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span> (replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/fsl-stats-replica.md') }}">fsl-stats-replica</a> (standard tier, FSL 6.0.7.23) · API <a href="{{ repo('docs/api/fsl-stats.md') }}">fsl-stats</a> · its companion: <a href="{{ link('/tools/fsl-maths/') }}">fslmaths</a></dd>
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

FSL is distributed under the FSL Licence, which allows non-commercial use only, so LARMORX keeps its FSL tools in two implementations: the exact replica translated from FSL's source, in the separate package `larmorx-nc` (`pip install larmorx-nc`), and a clean-room original in LARMORX itself, written from a behavioural specification without FSL's code. For fslstats only the replica exists so far: `larmorx fsl fslstats` and `lx.fsl.fslstats` run it when `larmorx-nc` is installed, and a clear error names the package otherwise. The replica follows FSL 6.0.7.23 and needs no FSL installation; it lives in `larmorx-nc`'s shared core, beside the image statistics FAST and BET use, with nlohmann/json 3.12.0's number formatting for `-json`. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

fslstats prints numbers, so the question for the replica is whether it prints FSL's text, character for character, with FSL's messages and exit status.

{{ ev.agreement('fsl-stats', 'replica') }}

The record runs 208 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-stats-replica.md)): 172 print FSL's text byte for byte, and in 36 FSL refuses the input or stops and the replica does the same, with the same message and exit status (*rejected by both*). They cover fMRIPrep's four goodvoxels calls, BET's call on fMRIPrep's preprocessed T1w, FSL's own tests of fslstats (each option in text and in JSON, against FSL's expected outputs as well), every option in every data type and in combination, the options' order, `-t`, `-K` and `-json`, every message and failure case, and the defects LARMORX corrects by default: each case also runs the replica's default mode, which names every correction where it changes the output (below).

## In fMRIPrep: the goodvoxels mask {#goodvoxels}

The four numbers fMRIPrep's goodvoxels workflow reads between its fslmaths calls, on ds005040's BOLD series in T1w space ([the fourteen fslmaths calls](/tools/fsl-maths/#goodvoxels)): FSL 6.0.7.23's printed text, and the replica's in both modes. fMRIPrep divides the coefficient-of-variation images by the two means and thresholds the modulated one at its mean plus half its standard deviation. The oracle runs have no FreeSurfer reconstruction, so the cortical ribbon is a stand-in, the segmentation's grey matter.

{{ ev.table('fsl-stats', 'goodvoxels') }}

## Every option on a real image {#options}

Each option once on real data, as a pipeline would call it: FSL's mean and standard deviation of ds005040's BOLD series in T1w space, the series itself (63 volumes) for `-t`, fMRIPrep's brain mask for `-k`, fMRIPrep's segmentation (grey matter, white matter, CSF) at each BOLD voxel for `-K`, and BET's call on fMRIPrep's preprocessed T1w. The replica prints FSL's text in every one. Its default mode differs where a correction applies: without a mask, FSL squares each value of `-S` in single precision, so its standard deviation of the nonzero voxels is 29842.182847 where `-s` gives 29842.182845 for the same voxels; the default takes the masked form and prints the latter (FSL-182, named).

{{ ev.table('fsl-stats', 'options') }}

## Random testing {#random}

Differential random testing's trial of this part (shared with fslmaths): random option lists on random images, each run by FSL 6.0.7.23 (through the oracle cache) and by the replica, the printed text compared.

{{ ev.table('fsl-stats', 'trial') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, its verdict and the reason. Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('fsl-stats') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default and warns, with `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) giving FSL's output byte for byte where FSL's is defined ([register](repo:docs/findings/upstream-defects.md)); where FSL crashes, the replica refuses in both modes or gives a defined result. NaN values are left out of the order statistics: `-R`, `-x`, `-X`, the percentiles, the histograms and the robust range (FSL-181). Without a mask, `-s` and `-S` take the masked forms: the variance clamped at 0 and 0 for a single value, `-S`'s squares in double precision (FSL-182). With `-t`, a 4D `-k` or `-d` image gives each time point its volume (FSL-183). `-x` and `-X` of a mask without voxels are refused in both modes, where FSL crashes (FSL-184). `-e` and `-E` of an image whose robust range is empty give the entropy 0 instead of crashing (FSL-185). `-H` with a maximum not above its minimum is an error, where FSL prints nothing (FSL-186). A value more than about two billion bin widths above a histogram's range counts in its last bin (FSL-187: `-H`, `-e`, `-E`, `-r`; shared with fslmaths, BET and FLIRT). `-w` of a 4D image without nonzero voxels gives the whole time range (FSL-188). `-json` writes voxel counts exactly, where FSL rounds them to single precision above 16,777,216 (FSL-189).

## Known limits {#limits}

The replica is experimental. The record's standard tier holds fMRIPrep's and BET's calls; its full tier, the data panel and long random testing run in the final validation phase. The goodvoxels calls use a stand-in for the cortical ribbon, to be checked again with a real ribbon once an fMRIPrep run with FreeSurfer's reconstruction exists. Images compressed with zstd or bzip2 are decompressed whole before they are read. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). There is no benchmark report yet: speed is measured with the clean-room original.
