---
title: fslstats
kicker: Evidence · FSL
lede: >-
  `fslstats` prints statistics of an image: its mean, standard deviation, extremes, robust range,
  percentiles, entropy, voxel count and volume, centre of gravity, bounding box or histogram, per
  volume, per label or as JSON. fMRIPrep's goodvoxels mask reads four of its numbers, and BET's
  script one. The replica (`larmorx-nc`) prints FSL 6.0.7.23's text byte for byte, with its
  messages and exit status, in all 172 of its compared cases, out of 208. The clean room
  (`larmorx`) is within its record's thresholds in all 126 of its compared cases, out of 162, and
  prints FSL's numbers in 125 of them, fMRIPrep's goodvoxels calls among them; the other is BET's
  call, within the record's bound (6 × 10⁻⁸ relative).
description: >-
  How LARMORX's two ports of FSL's fslstats, a replica and a clean room, compare with FSL 6.0.7.23:
  fMRIPrep's goodvoxels calls and BET's call, every option on a real image with -t, -K and -json,
  FSL's own tests (the replica), every case of both records with its verdict, both ports'
  random-testing runs with the clean room's triage, and the speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx-nc</code> <span class="port-licence">FSL Licence: non-commercial use only</span>: translated from FSL 6.0.7.23's source (fsl-avwutils 2209.6, with fsl-newimage 2601.0's statistics and nlohmann/json 3.12.0's number formatting); it runs as a separate program</li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crate <code>larmorx-fsl</code>, written from <a href="{{ repo('specs/fslstats.md') }}">specs/fslstats.md</a>, FSL's usage text and documentation and runs of FSL 6.0.7.23, without FSL's source (2026-11-03 and 04)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--experimental">experimental</span>; clean room <span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/fsl-stats-replica.md') }}">standard comparison</a> (FSL 6.0.7.23) · the clean room's: <a href="{{ repo('docs/validation/fsl-stats.md') }}">standard comparison</a> (FSL 6.0.7.23) · benchmark <a href="{{ repo('docs/benchmarks/fsl-maths.md') }}">fsl-maths</a> (with fslmaths)</dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/fsl-stats.md') }}">fsl-stats</a> · its companion: <a href="{{ link('/evidence/fsl-maths/') }}">fslmaths</a></dd>
</dl>

## What is compared {#what-it-is}

`fslstats [-t] [-K <labels>] [-json] <image> [options]` prints statistics of an image. The options act in their order. Some change what the options after them see:

- `-l` and `-u` set lower and upper thresholds, `-k` a mask, `-d` a difference image;
- `-a` takes absolute values, and `-n` turns NaN into 0.

The others print a number or a few:

- `-m`, `-M`: the mean, and the mean of the nonzero voxels; `-s`, `-S`: the standard deviation, likewise;
- `-R`: the minimum and maximum; `-r`: the robust range, 2 % and 98 %; `-p`, `-P`: percentiles;
- `-e`, `-E`: the entropy; `-v`, `-V`: voxels and volume;
- `-w`: the smallest box holding the nonzero voxels; `-x`, `-X`: the maximum's and the minimum's voxels;
- `-c`, `-C`: the centre of gravity, in mm and in voxels; `-h`, `-H`: histograms.

`-t` prints one line per volume, `-K` one per label of an index image, `-json` everything as JSON. Numbers print with six decimals, as nipype reads them.

fMRIPrep reads four of them in its goodvoxels mask (`--project-goodvoxels`): `-M` and `-S` of the ribbon's coefficient of variation, before and after its modulation. BET's script reads one, `fslstats <image> -l <t> -C`, its starting centre; LARMORX's BET replica runs it through this code.

The two ports run beside FSL 6.0.7.23's `fslstats` on the same files with the same arguments, and their printed text is compared with FSL's.

```bash
larmorx fsl fslstats cov_ribbon.nii.gz -M -S
larmorx fsl fslstats -t -K labels.nii.gz bold.nii.gz -M
```

The first prints the mean and standard deviation of an image's nonzero voxels, as fMRIPrep reads them. The second prints, volume by volume, the mean of each label's nonzero voxels.

```python
import larmorx as lx

text = lx.fsl.fslstats("cov_ribbon.nii.gz", "-M", "-S")   # the command line's options: its standard output
mean = lx.fsl.image_mean("cov_ribbon.nii.gz", nonzero=True)  # one typed wrapper per statistic: numbers
```

The calls above leave `implementation` at `"auto"`. The [API page](repo:docs/api/fsl-stats.md) describes the generic function and the typed wrappers. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

FSL comes under the FSL Licence, which allows non-commercial use only. So LARMORX has two ports of its FSL programs. The replica is translated from FSL's source and lives in its own package, `larmorx-nc` (`pip install larmorx-nc`). The clean room is in `larmorx` itself. It is written without FSL's code, from fslstats' behavioural specification ([specs/fslstats.md](repo:specs/fslstats.md)), FSL's usage text and documentation and runs of FSL 6.0.7.23 as a black box.

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). On the command line, `larmorx --implementation clean-room fsl fslstats ...` does the same from the next release; in 0.1.0rc1 it is the environment variable `LARMORX_IMPLEMENTATION`. `auto`, and `larmorx fsl fslstats`, take the replica when `larmorx-nc` is installed, else the clean room.

The replica follows FSL 6.0.7.23 and needs no FSL installation. It lives in `larmorx-nc`'s shared core, beside the image statistics FAST and BET use, with nlohmann/json 3.12.0's number formatting for `-json`.

The clean room has every option and preoption (`-t`, `-K`, `-json`), every message, exit status and failure case (a crash's lost buffered output included), and the defects with their switches. It prints `-json`'s numbers in nlohmann's format as the specification describes it. Its passes run in parallel, the masked sums in FSL's blocks added in order, so its text is the same at any thread count; it holds one copy of the image. Where the specification leaves a convention open, it follows FSL's as black-box runs measured it (findings 21 and 28 of its [findings](repo:docs/findings/fsl-maths-original.md)).

**The C library's last digits (since 2026-11-04).** fslstats' entropies (`-e`, `-E`) take logarithms from glibc, the C library of Linux, whose results are now and then one unit in the last place away from the exact value rounded once. LARMORX computes them correctly rounded, the same on every platform. Since 2026-11-04 the clean room's `reproduce` computes them exactly as glibc 2.35 does, and its default, `fix`, correctly rounded, naming GLIBC-07 exactly where the printed number would differ ([register](repo:docs/findings/upstream-defects.md)). On every case of its record the printed numbers, to their six digits, are the same either way: no number of the record moved.

## The verdicts at a glance {#verdicts}

fslstats prints numbers. The question for the replica is whether it prints FSL's text, character for character, with FSL's messages and exit status.

{{ ev.agreement('fsl-stats', 'replica') }}

The replica's record runs 208 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-stats-replica.md)). 172 print FSL's text byte for byte. In 36 FSL refuses the input or stops, and the replica does the same, with the same message and exit status (*rejected by both*). The cases cover:

- fMRIPrep's four goodvoxels calls, and BET's call on fMRIPrep's preprocessed T1w;
- FSL's own tests of fslstats: each option in text and in JSON, against FSL's expected outputs as well;
- every option in every data type and in combination, the options' order, `-t`, `-K` and `-json`;
- every message and failure case;
- the defects LARMORX corrects by default. Each case also runs the replica's default, `fix`, which names every correction where it changes the output ([below](#corrections)).

The clean room is written without FSL's source, so its record holds it to [specs/fslstats.md](repo:specs/fslstats.md) §10 instead:

- the counts, extremes, coordinates, the robust range, percentiles, histograms, `-w` and the masked means and standard deviations identical to FSL's;
- the other numbers (the unmasked means and standard deviations, `-D`, the entropies, the centres of gravity) within 10<sup>−6</sup> relative;
- its messages and exit status FSL's.

{{ ev.agreement('fsl-stats', 'original') }}

The clean room's record runs 162 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-stats.md)): the replica suite's cases but FSL's own tests (they read FSL's source tree, which a clean-room implementer does not open) and the replica's three random-testing cases, BET's call among them, 9 of its own (`orig/`) and 4 permanent cases of random testing.

- **Bit-identical, 125.** They print FSL's numbers, with its messages and exit status. fMRIPrep's four goodvoxels calls are among them.
- **Open, 1.** BET's `-l 0.001 -C` on fMRIPrep's preprocessed T1w is within the bound: its x is 97.862248 against FSL's 97.862242, 6.1 × 10<sup>−8</sup> relative. The cause is the mapping back to millimetres of a neurological image, whose arithmetic in FSL a black box does not show.
- **Rejected by both, 36.** The same message and exit status.

## In fMRIPrep: the goodvoxels mask {#goodvoxels}

The four numbers fMRIPrep's goodvoxels workflow reads between its fslmaths calls, on ds005040's BOLD series in T1w space ([the fourteen fslmaths calls](/evidence/fsl-maths/#goodvoxels)). FSL 6.0.7.23's printed text, the replica's in `reproduce` and in `fix` and the clean room's in `reproduce` and in `fix` are the same, each of them. fMRIPrep divides the coefficient-of-variation images by the two means, and thresholds the modulated one at its mean plus half its standard deviation. The fMRIPrep runs have no FreeSurfer reconstruction, so the cortical ribbon is a stand-in, the segmentation's grey matter.

{{ ev.table('fsl-stats', 'goodvoxels') }}

## Every option on a real image {#options}

Each option once on real data, as a pipeline would call it: FSL's mean and standard deviation of ds005040's BOLD series in T1w space, the series itself (63 volumes) for `-t`, fMRIPrep's brain mask for `-k`, fMRIPrep's segmentation (grey matter, white matter, CSF) at each BOLD voxel for `-K`, and BET's call on fMRIPrep's preprocessed T1w.

- The replica prints FSL's text in every one.
- Its default, `fix`, differs where a correction applies. Without a mask, FSL squares each value of `-S` in single precision, so its standard deviation of the nonzero voxels is 29842.182847, where `-s` gives 29842.182845 for the same voxels. The default takes the masked form and prints the latter (FSL-182, named).
- The clean room prints FSL's text in every one but BET's call (its centre of gravity within §10's bound, [above](#verdicts)), at 14 threads and at one. Its default makes FSL-182's correction too, and names it.

{{ ev.table('fsl-stats', 'options') }}

## Random testing {#random}

The replica's random-testing run (2026-11-03), shared with fslmaths: random option lists on random images, each run by FSL 6.0.7.23 (through the cache of the original's runs) and by the replica, the printed text compared.

{{ ev.table('fsl-stats', 'trial') }}

The clean room's random-testing run (2026-11-03), beside fslmaths' and 20 minutes long: 150,000 random option lists, the preoptions and fMRIPrep's and BET's forms among them, each compared as the record compares. 149,214 agreed, and 7 differed only by a correction its default names. Of the 779 that differed, run again with the part's final build:

- 545 were the clean room's mistake, fixed with permanent cases: the histograms of `-h` and `-H` when no histogram is made;
- 74 were the suite's: §10's bound over a histogram's lines, and an output cut short;
- 160 are explained: `-c` and `-C` of images holding NaN and infinities, where FSL's NaN carries another sign (129), and the last printed digit at §10's bound (31).

None stays open.

{{ ev.table('fsl-stats', 'trial-original') }}

{{ ev.table('fsl-stats', 'trial-original-triage') }}

## Every case {#cases}

Each case of the two records, the replica's and the clean room's, both against FSL 6.0.7.23 (a column each), with what it tests, its command line, each port's verdict and the reason. The 13 cases only the clean room's record holds are its own: `orig/` and the permanent cases random testing gave it. Search, filter by category or verdict (or select a segment of a chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('fsl-stats') }}

## Speed {#speed}

Reading the image is most of fslstats' time.

- On BET's call on fMRIPrep's preprocessed T1w the clean room takes 0.45 s on one thread and 0.29 s on 14, against FSL's 0.58 s.
- On 63 volumes of a BOLD series (`-t -M -S -r`) it takes 0.22 s against FSL's 0.23 s, with less memory than FSL (41 MiB against 47).
- The replica takes 0.34 and 0.23 s.

These timings come from [the report](repo:docs/benchmarks/fsl-maths.md), shared with fslmaths. They are informal: one run each, on a machine running other work beside them.

{{ ev.speed('fsl-stats') }}

{{ ev.table('fsl-stats', 'benchmark') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default, `fix`, and warns. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives FSL's output byte for byte, where FSL's output is defined ([register](repo:docs/findings/upstream-defects.md)). Where FSL crashes, the replica refuses in `fix` and in `reproduce`, or gives a defined result.

- NaN values are left out of the order statistics: `-R`, `-x`, `-X`, the percentiles, the histograms and the robust range (FSL-181).
- Without a mask, `-s` and `-S` take the masked forms: the variance clamped at 0, and 0 for a single value; `-S`'s squares in double precision (FSL-182).
- With `-t`, a 4D `-k` or `-d` image gives each time point its volume (FSL-183).
- `-x` and `-X` of a mask without voxels are refused in `fix` and in `reproduce`, where FSL crashes (FSL-184).
- `-e` and `-E` of an image whose robust range is empty give the entropy 0 instead of crashing (FSL-185).
- `-H` with a maximum not above its minimum is an error, where FSL prints nothing (FSL-186).
- A value more than about two billion bin widths above a histogram's range counts in its last bin (FSL-187: `-H`, `-e`, `-E`, `-r`; shared with fslmaths, BET and FLIRT).
- `-w` of a 4D image without nonzero voxels gives the whole time range (FSL-188).
- `-json` writes voxel counts exactly, where FSL rounds them to single precision above 16,777,216 (FSL-189).

The clean room makes the same corrections by default, with the same notices (FSL-181 to FSL-189). Its `reproduce` follows FSL where FSL's output is defined. Where FSL crashes, its `reproduce` prints what FSL's buffer had written before the crash and ends with exit status 1.

## Known limits {#limits}

Both ports are experimental. The replica's record's standard comparison holds fMRIPrep's and BET's calls; its full comparison, the data panel and the long random-testing runs come in the final validation phase.

The clean room is held to §10's bound for the numbers FSL sums without a mask and for the centres of gravity (BET's call: 6 × 10<sup>−8</sup> relative). FSL's own tests of fslstats are not among its cases, as they read FSL's source tree; they may be run against it later, as a check outside the clean room.

The goodvoxels calls use a stand-in for the cortical ribbon. They are to be checked again with a real ribbon once an fMRIPrep run with FreeSurfer's reconstruction exists.

Images compressed with zstd or bzip2 are decompressed whole before they are read.

The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output. The benchmark is informal: one run each, on a shared machine.

## History {#history}

- **2026-11-03**: the replica, translated from FSL 6.0.7.23's source, its record of 208 cases and its random-testing run, 69,077 fslstats calls beside fslmaths'. The clean room, written from [specs/fslstats.md](repo:specs/fslstats.md), FSL's usage text and documentation and runs of FSL, and its random-testing run, 150,000 option lists in 20 minutes beside fslmaths'.
- **2026-11-04**: the clean room complete: every option ([the roadmap](/roadmap/)). Its `reproduce` computes the entropies' logarithms as glibc 2.35 does (GLIBC-07); no printed number of its record moved. The clean room's record, 162 cases, dates from that day.
