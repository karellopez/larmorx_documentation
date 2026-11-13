---
title: BET
kicker: Evidence · FSL
lede: >-
  `bet` finds the brain in a head image; `betsurf` adds the skull and the scalp. The replica
  (`larmorx-nc`) matches FSL 6.0.7.23's exit status, messages and files, byte for byte, in 201 of
  its 263 cases, and 47 more are rejected by both. Of the other 15, FSL crashes in 13 and reads
  memory beyond the image in one; the last needs fslpy's conversion of a file to another type,
  which the replica does not replicate yet. The clean room (`larmorx`) is within the thresholds
  in 198 of its 200 compared cases. Its brains, masks and outlines are FSL's bit for bit in 378
  of 380 images, and `betsurf`'s masks and outlines are within the thresholds in 114 of 116, 34
  of them bit for bit.
description: >-
  How LARMORX's two ports of FSL's BET (bet, bet2, betsurf, with bet -S, -B, -A and -A2,
  standard_space_roi and fslroi), a replica and a clean room, compare with FSL 6.0.7.23, FSL
  6.0.7.17 and fMRIPrep 25.2.6: fMRIPrep's skull strip of a real BOLD reference, a real T1w with
  -R, the skull and scalp surfaces, a three-year-old's BOLD reference from the data panel, the
  variations and standard_space_roi on seven real heads of the data panel, random testing of both
  ports with its triage, every case of the three records with its verdict, and speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx-nc</code> <span class="port-licence">FSL Licence: non-commercial use only</span>: translated from FSL's source; it runs as a separate program</li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crate <code>larmorx-fsl</code>, written from <a href="{{ repo('specs/bet.md') }}">specs/bet.md</a> and <a href="{{ repo('specs/standard_space_roi.md') }}">specs/standard_space_roi.md</a>, the BET paper and runs of FSL 6.0.7.23, without FSL's source</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span>; clean room <span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/fsl-bet-replica.md') }}">standard comparison</a> (FSL 6.0.7.23; <code>standard_space_roi</code> and <code>fslroi</code> in it), <a href="{{ repo('docs/validation/fsl-bet-replica-full.md') }}">full comparison</a> (FSL 6.0.7.17) · the clean room's: <a href="{{ repo('docs/validation/fsl-bet.md') }}">fsl-bet</a> (FSL 6.0.7.23) · benchmark <a href="{{ repo('docs/benchmarks/fsl-bet.md') }}">fsl-bet</a></dd>
<dt>Reference</dt><dd><a href="{{ link('/programs/fsl/bet/') }}"><code>bet</code></a>, <a href="{{ link('/programs/fsl/bet2/') }}"><code>bet2</code></a>, <a href="{{ link('/programs/fsl/betsurf/') }}"><code>betsurf</code></a> · API pages <a href="{{ repo('docs/api/fsl-bet.md') }}">fsl-bet</a>, <a href="{{ repo('docs/api/fsl-roi.md') }}">fsl-roi</a> (<code>standard_space_roi</code>, <code>fslroi</code>)</dd>
</dl>

## What is compared {#what-it-is}

BET finds the brain in a head image. A tessellated sphere (2562 vertices) is placed inside the head at its centre of gravity and deformed, a thousand times over, by three forces at each vertex: one along the surface that keeps the vertices evenly spread, one along the normal that keeps the surface smooth, and one along the normal that follows the intensities found inward, against a threshold between the image's robust minimum and the local maximum (`-f`). The brain is what the surface encloses.

`bet` is the script around it, with variations. `-R` repeats the extraction from the brain's own centre, `-F` applies the first volume's mask to a 4D series, and `-Z` pads an image that is short in z. `-S` and `-B` are SIENA's cleanups: the eyes and optic nerves; the bias field and the neck, through `standard_space_roi`, FLIRT, FAST, `fslmaths` and `fslstats`. `-A` and `-A2` add `betsurf`'s surfaces after a registration to MNI152. `betsurf` casts intensity profiles along the brain surface's normals through the T1 (and a T2) to find the inner skull, the outer skull and the scalp, and deforms three more surfaces onto them.

Both ports run beside FSL 6.0.7.23's programs, on the same files with the same arguments: `bet2`, the `bet` script with its variations, `betsurf`, and FSL's `standard_space_roi` and `fslroi`, which the variations run. The replica's full comparison runs FSL 6.0.7.17 too, the version it was first translated from.

fMRIPrep calls `bet` on every BOLD run's reference, `bet <boldref> <boldref>_brain.nii.gz -f 0.20 -m`, in niworkflows' first skull strip (`enhance_and_skullstrip_bold_wf`). Where field maps correct the distortion, it calls it once more on the corrected reference (`skullstrip_bold_wf`).

```bash
larmorx fsl bet boldref.nii.gz boldref_brain.nii.gz -f 0.20 -m
larmorx fsl betsurf --t1only -o -m -s T1w.nii.gz T1w_brain_mesh.vtk T1w_to_MNI152.mat T1w
```

```python
import larmorx as lx

r = lx.fsl.bet("boldref.nii.gz", frac=0.2, mask=True)     # implementation="auto"
r.brain, r.mask
s = lx.fsl.betsurf("T1w.nii.gz", lx.fsl.bet("T1w.nii.gz", mesh=True).mesh, "T1w_to_MNI152.mat")
```

### Its two ports {#ports}

FSL comes under the FSL Licence, which allows non-commercial use only. So LARMORX has two ports of its FSL programs. The replica is translated from FSL's source and lives in its own package, `larmorx-nc` (`pip install larmorx-nc`). The clean room is in `larmorx` itself. It is written without FSL's code, from a description of what the programs do ([specs/bet.md](repo:specs/bet.md)), the BET paper and runs of FSL's programs.

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). On the command line, `larmorx --implementation clean-room fsl bet ...` does the same from the next release; in 0.1.0rc1 it is the environment variable `LARMORX_IMPLEMENTATION`. `auto` takes the replica when `larmorx-nc` is installed, else the clean room.

The replica follows FSL 6.0.7.23. It was translated from 6.0.7.17's source, and what changed between the two is in its findings (History, below). It runs none of FSL's programs and needs no FSL installation. Its FSL libraries are those every FSL replica of `larmorx-nc` shares: newimage, NewNifti, meshclass, and the C library's maths as FSL's Linux build calls it.

The clean room follows FSL 6.0.7.23 as well and is built for speed. Every parallel step runs in the call's own pool of threads, with the same result at any thread count. Its memory peak is FSL's or lower on every measured call but `bet -R`: 117 MiB, against FSL's 103; 13 of the 117 are Python's own. Its smoothness weight's `tanh` is glibc's by default, as FSL's is, and the correctly rounded one on request (`--tanh correctly-rounded`), a decision of the project recorded with [GLIBC-06](repo:docs/findings/upstream-defects.md#summary) in the register.

The replica runs `bet -S`, `-B`, `-A` and `-A2`: FSL's script for each, with every program the script runs the replica's own, called in the same process ([below](#options)). FSL's `standard_space_roi` and `fslroi` are programs of their own ([below](#ssroi)), and the three standard images they read are shipped inside `larmorx-nc` ([below](#data)).

The clean room runs them as well, written from the specifications ([specs/bet.md](repo:specs/bet.md) §5.3, [specs/standard_space_roi.md](repo:specs/standard_space_roi.md)): FSL's script for each, in the same process. Every program the script runs is the clean room's own: `bet2`, FLIRT, FAST, `fslmaths`, `fslstats`, `dc`'s arithmetic, `standard_space_roi`, `fslroi` and `betsurf`. Its data search finds the standard images ([below](#data)). How to read what follows: [how to read the evidence](/validation/#reading).

**The C library's last digits.** `bet2`'s radius and its surface's deformation take powers (`powf`), and `betsurf`'s smoothing takes `exp`, from glibc, the C library of Linux. glibc's results are now and then one unit in the last place away from the exact value rounded once. LARMORX computes them correctly rounded, the same on every platform. The clean room's `reproduce` computes them exactly as glibc 2.35 does, and its `fix` (the default) correctly rounded. This is GLIBC-07 in the [register](repo:docs/findings/upstream-defects.md), and no notice names it: whether a fitted surface moved with such last bits cannot be told without running it twice (a decision of the project of 2026-11-04, recorded with GLIBC-07). No number of the clean room's record moved, and its runs of the examples below give the same bytes as before.

## The verdicts at a glance {#verdicts}

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes. Its two records answer it: the full comparison against FSL 6.0.7.17 (the first chart) and the standard comparison against FSL 6.0.7.23 (the second).

{{ ev.agreement('fsl-bet', 'replica') }}

{{ ev.agreement('fsl-bet', 'replica-23') }}

The full comparison runs 173 cases against FSL 6.0.7.17. In both records, every compared case gives FSL's files byte for byte. The standard comparison, which runs again before every change goes into the published code, runs 263 cases against FSL 6.0.7.23: 159 of the full comparison's cases, the new cases of 6.0.7.23 (`--binaryMask`, the zstd and bzip2 formats) and of random testing, `-S`, `-B`, `-A` and `-A2` (on synthetic heads with every option they pass on, `-d` and `-v`, and on six real heads), `standard_space_roi` (25 cases) and `fslroi` (26). Of the 263, 201 pass (FSL's files byte for byte, with its exit status and messages), 47 are rejected by both, 15 are expected divergences, and none fails.

Each of its cases also runs FSL 6.0.7.17 on the same arguments and says what changed between the two versions, and why: the build string in every image's header, the usage text, the new options and formats, FSL-41's fix (a binary image), and one case where FSL's fill reads memory beyond the volume (FSL-43). Nothing else changed.

Wherever FSL writes files, the replica writes the same files byte for byte (images: header and data; meshes as text), with FSL's exit status and messages. That holds on fMRIPrep's 29 calls in the twelve of its runs that have BOLD runs (the data panel's included), every option of `bet2`, `bet` and `betsurf`, every storage type and file format FSL reads, and synthetic heads with a known brain. It holds on real T1w images from a child of 3 years to an adult of 82, at 1.5 T, 3 T and 7 T, a tumour and a stroke (with `-R` too), and on `betsurf` with real T1w and T2w images from FLIRT's registrations: 364 files of 364 byte for byte (against FSL 6.0.7.23: 600 of 600).

Where FSL refuses the input, so does the replica, with FSL's message (*rejected by both*). Where FSL crashes on what it leaves undefined (a constant image, a mesh file it reads without checks, a surface whose centre is not a number), `fix` refuses with the reason. `reproduce` keeps everything FSL defines, fills the rest deterministically and names the defect (*expected divergence*). One more case is an expected divergence: `standard_space_roi` copying an input of another file type than `FSLOUTPUTTYPE`'s, which fslpy's `imcp` converts with nibabel. The replica does not replicate that conversion yet and refuses it clearly, in both modes. Each case also runs with `fix`, where LARMORX corrects FSL's deterministic defects and names them. NaN and infinite voxels give FSL's NaN bits on every platform: the replica computes them with x86-64's rules, checked with ARM's, emulated.

Random testing draws `bet2`'s, `bet`'s and `betsurf`'s options on random heads of every stored type and runs them through the same comparison ([how random testing works](repo:docs/validation/difftest.md)). Its first runs found eight kinds of difference, every one fixed, and seven are kept as cases of the record (`difftest/...`). Its run after the version update, against FSL 6.0.7.23, left six, each replayed against both versions:

- two were the replica's: a mask's fill that starts outside the image, which FSL makes through the image's linear index and so reaches its voxels (FSL-43);
- two were mistakes of the comparison itself;
- one is a defect of FSL's own (FSL-63: `bet -R` loses a leading `-e`, through bash's `echo`);
- one is where FSL's fill reads memory beyond the volume (FSL-43, undefined).

Six cases of the record keep them. Two more of that run's inputs met FSL 6.0.7.23's new matrix arithmetic ([Known limits](#limits)); the replica follows it, and two more cases of the record keep them: both agree. The replica needs no more memory than FSL in any call measured, a real T1w and a 240-volume BOLD series included.

The clean room is written without FSL's source, so its record holds it to thresholds ([specs/bet.md](repo:specs/bet.md) §11). Exit statuses and messages must be FSL's, and every file FSL writes either bit-identical or, for the masks, within a Dice coefficient and a boundary distance. `betsurf` deforms its three surfaces from thousands of profiles, so it is held to its masks (Dice ≥ 0.99, the boundary distance's 95th percentile ≤ 1 voxel), with its meshes reported. A case is *bit-identical* when every value of every file is FSL's, and *open* when a file only meets its threshold, or misses it.

{{ ev.agreement('fsl-bet', 'original') }}

The clean room's record ([fsl-bet](repo:docs/validation/fsl-bet.md), 252 cases) runs the replica's standard cases against FSL 6.0.7.23, `betsurf`'s real heads, and the variations, `standard_space_roi` and `fslroi`. 198 of its 200 compared cases are within the thresholds. 46 more are rejected by both alike. In 6, FSL crashes, and `reproduce` fills in what FSL leaves undefined.

`bet2` and `bet` give FSL's files bit for bit: 378 of 380 brains, masks and outlines, and every skull image and mesh, the surfaces that FSL reruns after a self-intersecting first pass included. fMRIPrep's calls in its runs are bit-identical: 58 of 58 outputs with fMRIPrep's own values.

`betsurf` decides its profiles as FSL does: 330 of 330 single profiles, probed one at a time with a triangle so small that it casts a single profile. Where many profiles vote, its surfaces are FSL's. Where few do (a skull base where nearly every profile is set aside), the inner skull settles a few millimetres elsewhere on a few vertices, and the scalp differs a little everywhere. 34 of its 116 masks and outlines are FSL's bit for bit, and 80 more are within its thresholds. The scalp of a Philips scan with its T2 misses them (the boundary's 95th percentile is 2 voxels). The other case the clean room misses is `bet -B` on the 3.5-year-old's head: its `-c` start, on an image stored in neurological order, parts a few bits from FSL's (an open question of the specification).

A random-testing run of 1,846 random calls found two kinds of difference left. One is `betsurf`'s decisions on small synthetic heads whose profiles leave the image. The other is a centre given or measured on an image stored in neurological order (`-c`, `bet -R`), which starts `bet2` a few bits elsewhere; stored the other way, the same image gives FSL's result exactly. Both are open questions for the specification ([findings](repo:docs/findings/fsl-bet-clean-room.md)). The worked examples below show the clean room's runs beside FSL's and the replica's.

## In fMRIPrep: the BOLD reference's skull strip {#example}

fMRIPrep's own call, from one of its runs. It is given to FSL 6.0.7.17, FSL 6.0.7.23 and fMRIPrep's build of FSL (with newer image libraries), beside the files fMRIPrep's node wrote. Then it is given to the replica, compared with FSL 6.0.7.17 and with FSL 6.0.7.23, and to the clean room, with `fix` and with `reproduce`, compared with FSL 6.0.7.23. Each panel names its version, and *FSL bet 6.0.7.23 − FSL bet 6.0.7.17* is FSL's own step between the two. The masks are drawn over the image they were made from. Choose *Brain* above the panels for the extracted brain, and a difference panel for what separates two runs.

{{ ev.example('fsl-bet', 'fmriprep-bet') }}

## A real T1w with `-R` {#t1w}

The anatomical use, with the robust centre estimation. The `bet` script runs `bet2`, measures the brain's centre of gravity (`fslstats -C`), runs `bet2` again from it, and stops when the centre moves less than a voxel. The image is shown only inside the brain masks. FSL 6.0.7.17 and 6.0.7.23, the replica and the clean room each run the whole script.

{{ ev.example('fsl-bet', 't1w-robust') }}

## The skull and the scalp: `betsurf` {#betsurf}

`betsurf` with a T2 (the call `bet -A2` makes after its registrations), on a synthetic head, which shows the three surfaces whole: on a real head that was not defaced, the scalp would show a face. The replica's full comparison compares `betsurf` on real T1w and T2w images as well (a child, an adult of 82, a tumour, a Philips scanner), from FLIRT's registrations, byte for byte. Real heads whose faces their datasets removed show the surfaces too: `bet -A` and `-A2` on two heads of the data panel, [below](#option-a). On this head the clean room's three surfaces lie within half a millimetre of FSL 6.0.7.23's (95 % of their vertices within 0.006 mm), and its masks differ in a few voxels. Its record measures the real heads.

{{ ev.example('fsl-bet', 'betsurf-head') }}

## On the data panel: a three-year-old's BOLD reference {#panel}

The data panel's youngest subject (ds000228, aged 3.5: a small head, an oblique field of view), through fMRIPrep's BET call. The record runs the call on every run of the panel that has BOLD runs. As a panel case beside the examples above, it is stored as three full-resolution slices, and the crosshair moves through them.

{{ ev.example('fsl-bet', 'panel-ds000228-child') }}

## The variations that run FSL's other programs: `-S`, `-B`, `-A`, `-A2` {#options}

Four of the script's variations run other FSL programs.

- `-S` removes the eyes and optic nerves, one of SIENA's cleanups. It runs `bet2` for the raw brain and skull, `standard_space_roi` to cut the head to MNI152's dilated brain mask and `bet2` again on it, FLIRT to bring MNI152's eye mask into the head, `fslmaths`' morphology, `fslstats`' mean and standard deviation of the brain, and `dc` for a threshold 3.5 deviations above it.
- `-B` removes the bias field and the neck, SIENA's other cleanup. It runs `standard_space_roi`, FAST's bias field, `fslmaths` to divide it out, `standard_space_roi` again and the script itself with `-R`; with `-s`, `standard_space_roi -maskFOV` and `bet2` for the skull.
- `-A` and `-A2` register the head to MNI152 with FLIRT and give `bet2`'s mesh to `betsurf` (`-A2` with the T2w, which FLIRT first registers to the T1w).

The replica runs FSL 6.0.7.23's script for each. Every program it runs is the replica's own, called in the same process with the words bash would give it, with the script's temporary files (`-d` keeps them), messages and exit statuses; GNU `dc`'s arithmetic for `-S`'s threshold is replicated too. Its record compares them on synthetic heads (every option they pass on, `-d`, `-v`, and the order of the variations: the last one given wins) and on the six real heads of the data panel shown below. Each passes, with every file FSL writes byte for byte.

Each example shows FSL 6.0.7.23's run (the record's own, from the cache of the original's runs) and the replica with `fix` and with `reproduce`. For `-S` and `-B` it also shows FSL's `bet` without the option on the same head (`-m`, with `-s` where the option writes a skull image). That comparison, *with and without* the option, is FSL against FSL: it shows the option's effect and has no verdict. These heads were defaced by their datasets (checked in LARMORX's test-data panel), so the whole field of view is shown, as three full-resolution slices through the crosshair.

The replica's `fix` differs from FSL only where it names a correction of a program the script runs. In both `-B` examples that is FAST's class variances (FSL-202, the cancellation in FAST's single-precision statistics), from which `-B`'s bias field comes, so the unbiased head and the brain bet finds in it move a little. FLIRT's integer output inside `standard_space_roi` (FSL-09) is named on two heads.

Each example also shows the clean room on the same call, with `fix` and with `reproduce`, every program the script runs its own (`bet2`, FLIRT, FAST, `fslmaths`, `fslstats`, `standard_space_roi`, `betsurf`), with its comparisons after the replica's. Its `reproduce` gives FSL 6.0.7.23's values, every one, on `-S` (both heads), on the 82-year-old's `-B` and on `standard_space_roi`. On the 3.5-year-old's `-B` its brain differs in 2,439 of 6,488,064 values. This is the record's one failure among these: the robust centre, on this image stored in neurological order, starts `bet2` a few bits elsewhere (an open question of the specification). On `-A` and `-A2`, `betsurf`'s masks differ at their edges (Dice 0.9993 to 0.9996; the scalp the most), as `betsurf`'s own record shows. Its `fix` differs from FSL where it names a correction (FSL-09, FSL-182, FSL-202). It also differs where it computes the C library's maths functions correctly rounded instead of as glibc does (GLIBC-07, which no notice names): FLIRT's rotations inside `standard_space_roi` and `betsurf`'s smoothing move a little with them.

### `-S`: the eyes and optic nerves {#option-s}

{{ ev.example('fsl-bet', 'bet-S-adult') }}

{{ ev.example('fsl-bet', 'bet-S-tumour') }}

### `-B`: the bias field and the neck {#option-b}

{{ ev.example('fsl-bet', 'bet-B-child') }}

{{ ev.example('fsl-bet', 'bet-B-older') }}

### `-A` and `-A2`: the skull and the scalp {#option-a}

On real heads `betsurf`'s three surfaces show whole: the inner skull, the outer skull and the scalp, as masks drawn over the T1w, with the skull between them (`betsurf -s`). Choose the mask above the panels.

{{ ev.example('fsl-bet', 'bet-A-older') }}

{{ ev.example('fsl-bet', 'bet-A2-child') }}

## standard_space_roi and fslroi {#ssroi}

`standard_space_roi` is FSL's script that cuts a head with a region of the standard space. FLIRT registers the head to MNI152 (or another reference, `-ssref`), and `convert_xfm` inverts the matrix. A mask (`-maskFOV`, `-maskMASK`, `-maskNONE`) and a region (`-roiFOV`, `-roiMASK`, `-roiNONE`) are brought back into the head with FLIRT's `-applyxfm`, then applied with `fslmaths` and `fslroi`. `-b` is MNI152's dilated brain mask, thresholded: the call `bet -S` and `-B` make. `fslroi` takes a box or a range of volumes out of an image (`bet -F` and `-Z` use it).

Both ports have both programs. The replica's are from FSL 6.0.7.23 (fsl-flirt 2111.4, fsl-avwutils 2209.6), as programs of `larmorx-nc`: `larmorx fsl standard_space_roi`, `larmorx fsl fslroi`; `lx.fsl.standard_space_roi`, `lx.fsl.fslroi` ([their API page](repo:docs/api/fsl-roi.md)). fslpy's `imcp` and `immv`, which the scripts call, are replicated with them. The clean room's (`implementation="clean-room"`, `"original"` in 0.1.0rc1; Apache-2.0) are written from [specs/standard_space_roi.md](repo:specs/standard_space_roi.md) and built for speed.

The clean room's cases are in its record. Of `fslroi`'s 26, 24 give FSL's files bit for bit and 2 are rejected by both alike. Of `standard_space_roi`'s 25, 17 are within the specification's thresholds and 8 are rejected by both alike. The thresholds: its files FSL's where its FLIRT gives FSL's matrix; else the masks' Dice ≥ 0.995 and the output's box within one voxel, and, given FSL's matrix, every file bit for bit. The six real heads are bit for bit.

The replica's record holds their cases beside bet's ([the record](repo:docs/validation/fsl-bet-replica.md)). `standard_space_roi`'s 25 cover every option on synthetic heads, every output type, the failures, and six real T1w and T2w heads: 16 give FSL's files byte for byte, 8 are rejected by both alike, and 1 is the expected divergence above (fslpy's conversion with nibabel). `fslroi`'s 26 cover every argument form, data type, header and format: 24 give FSL's files byte for byte and 2 are rejected by both.

Four defects of the script and two of `fslroi` are corrected or refused by `fix`, each named, with `reproduce` giving FSL's behaviour ([Corrections](#corrections), below). The example: `-b` on the data panel's youngest head, whose small size makes its registration to an adult template harder.

{{ ev.example('fsl-bet', 'ssroi-child') }}

## The standard images the variations read {#data}

`-S`, `-B` and `standard_space_roi` read FSL's MNI152 T1 at 2 mm and its dilated brain mask, `-S` its eye mask, and `-A` and `-A2` the T1 again (FLIRT's reference). These are three files of FSL 6.0.7.23's `fsl-data_standard` 2208.0 package, 1,420,897 bytes in all ([findings](repo:docs/findings/fsl-bet.md), written from FSL's source: for the replica's authors). FAST's `-b` reads no tissue priors, and `betsurf` no image of its own.

`larmorx-nc` ships these three files byte for byte, with FSL's licence (the package is part of FSL, under its non-commercial terms), the MNI ICBM 152 notice and a manifest of each file's origin, size and SHA-256, which a test checks. The wheel installs them beside the program, so the variations run without an FSL installation. The replica reads them from `LARMORX_FSL_DATA` when it is set, else from `$FSLDIR/data` as FSL's script does, else from its own copy. When none has them, it refuses before running anything, naming the missing image.

The clean room never ships them, since `larmorx` is Apache-2.0. It reads them as data from the first of these that has them: a directory named on its call or by `LARMORX_FSL_DATA`; `larmorx-nc`'s copy, when that package is installed; `$FSLDIR/data`; or a cache filled once by `larmorx fetch fsl-standard`. That command downloads FSL's `fsl-data_standard` 2208.0 package, checks it against its checksum and keeps only the three images (in `LARMORX_DATA_DIR`, else the platform's user cache directory).

## Random testing of both ports {#trial}

A random-testing run on 2026-11-05, after the clean room gained the variations, ran both ports on 909 random calls of `bet2`, `bet` with every variation, `betsurf`, `standard_space_roi` and `fslroi`, on random heads of every stored type ([how random testing works](repo:docs/validation/difftest.md)). The replica gave FSL's bytes on 896. Its 13 others are where FSL's FLIRT crashes inside `standard_space_roi` (FSL-75, a corrupted heap). The clean room had 114 differences, each in one category below, every one replayed with the final build. 20 are fixed: FLIRT's search kept its starting points of equal cost in the order found, where FSL sorts them, and on small heads every cost ties at the coarse scales. The others are open, each with its numbers and reproducer.

{{ ev.table('fsl-bet', 'trial-catchup') }}

{{ ev.table('fsl-bet', 'trial-catchup-triage') }}

## Every case {#cases}

Each case of the three records, with what it tests, its command line, its verdict and the reason: the replica's full comparison against FSL 6.0.7.17, its standard comparison against FSL 6.0.7.23, and the clean room's record against FSL 6.0.7.23, a column each. Search, filter (or select a segment of a chart above) and sort; `#case=<name>` links to one case.

{{ ev.cases('fsl-bet') }}

## Speed {#speed}

The wall time of the whole command, the median of three runs, on fMRIPrep's call, `bet2 -m` on real T1w images, and `betsurf` on real heads, with and without a T2 ([benchmark](repo:docs/benchmarks/fsl-bet.md)). FSL's programs run on one thread; the clean room's work runs in parallel, with the same result at any thread count.

{{ ev.speed('fsl-bet') }}

## Corrections by default {#corrections}

Both ports correct FSL's deterministic defects with `fix`, the default, and warn. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives FSL's behaviour byte for byte ([register](repo:docs/findings/upstream-defects.md)).

Among the corrections:

- `bet2` removes `.hdr` from a name wherever it stands (FSL-40).
- A mask's fill can start outside the image (FSL-43: on a single slice; FSL then reaches the image's voxels through its linear index, and memory beyond it).
- The `bet` script splits names with blanks (FSL-44), leaves `-Z`'s outputs padded when FSL is not on the `PATH` (FSL-45), removes files it did not create (FSL-46), and, with `-R`, loses a leading `-e` through bash's `echo` (FSL-63).
- One skull profile with an empty search range ends `betsurf` without a message or an output (FSL-50).
- `--t1only` exits 0 when it fails (FSL-54).
- An image with two or more extensions gets a wrong data offset (FSL-56).
- Since FSL 6.0.7.23, a name holding `.img` or `.hdr` opens another file (FSL-60), and `--ct` with `--binaryMask` converts the mask instead of the image (FSL-62).

Inputs that make no sense, which FSL uses silently, are refused by `fix` with a message naming the entry: NaN or meaningless numeric options (FSL-42), a T2 on another grid (FSL-48), a short matrix file (FSL-53), NaN inside the brain (FSL-55), and, since FSL 6.0.7.23, a `--binaryMask` on another grid than the input (FSL-61).

Where FSL crashes on what it leaves undefined, `fix` refuses, and `reproduce` fills it deterministically, with a warning: the median of an empty list (FSL-41: a constant or binary image; FSL 6.0.7.23 fixed it, taking the robust maximum), mesh values FSL never sets (FSL-52), and a fill from a centre that is not a number (FSL-43). Two of FSL's choices are kept and documented (FSL-49, FSL-57).

With the variations and the scripts they run:

- `-S`'s eye threshold is computed by `dc` from what `fslstats` prints, so a mean printed with an exponent or a minus sign becomes `dc` commands (FSL-216). `fix` reads the numbers as numbers, and refuses a mean that is not a number.
- `standard_space_roi` splits names with blanks (FSL-211), removes every file named like its temporary files (FSL-212), applies a `maskthr` it finds in the environment (FSL-213), and checks no step's status, going on after a failed program on missing files (FSL-214: `fix` refuses, stopping at the first failure).
- `fslroi` exits with status 0 after the errors it reports (FSL-215).
- `fslroi` and `fslmerge` write an int8 image as uint8 with the same bytes, so `bet -F` and `-Z` run `bet2` on the wrapped values (FSL-217: `fix` keeps int8).

Inside the variations, the corrections of the programs the script runs apply as in each program (FLIRT's FSL-09 and FSL-14, `fslstats`' FSL-182, FAST's FSL-202), named where they change a value.

## Known limits {#limits}

The clean room is experimental:

- `betsurf`'s surfaces differ from FSL's where few profiles vote and at the scalp; one real head's scalp misses its threshold.
- A centre on an image stored in neurological order can start `bet2` a few bits elsewhere (the 3.5-year-old's `-B`).
- `standard_space_roi`'s output header, on random headers, is one float unit from FSL's in its translation; or a form's translation is whole voxels apart where the qform and sform differ; or it is in single precision where FSL writes NIfTI-2. fslpy's conversion of an input of another file type is not yet checked byte for byte.
- `-B` and `-A2` on tiny heads, where FSL's script fails midway, print other messages.

These wait for answers in its specification or for BET's next clean-room part ([findings](repo:docs/findings/fsl-bet-clean-room.md)).

The replica does not replicate fslpy's `imcp` conversion of an image to another file type with nibabel (`standard_space_roi` with `-maskNONE -roiNONE` on an input whose type is not `FSLOUTPUTTYPE`'s), which it refuses clearly in both modes. Its short random-testing run of 2,699 random calls (of `bet2`, `bet` with every variation, `betsurf`, `fslroi` and `standard_space_roi`) met it 8 times; 2,580 calls agreed, and 70 differed only by a notice. Its other differences were two notices of the replica's own, fixed with permanent cases; the corrections inside the programs, which change only intermediate values there; and FLIRT's buffer overrun on constant and tiny images (FSL-75), after which FSL's FLIRT crashes or finishes as its memory's layout decides ([findings](repo:docs/findings/fsl-bet.md), written from FSL's source: for the replica's authors).

fMRIPrep's image has no `dc`, so its own `bet -R` and `-Z` stop there, and the T1w example shows no run of it.

FSL 6.0.7.23 computes the inverses, solves and determinants of its 4 × 4 matrices through LAPACK (Armadillo 14.2.1 on OpenBLAS 0.3.33), where 6.0.7.17 used closed forms, so the last bits change. The replica follows that arithmetic, checked bit for bit against FSL's own library on 30.2 million seeded matrices of 22 kinds (random, affine, rigid, diagonal, triangular, singular, and with NaN and infinite entries, among others). Random testing had found the change in `bet2`'s `-c` on an image stored in neurological order (a slightly different start, 18 of 15,360 voxels) and in `fslstats -C`'s sign of zero under `bet -R` on a one-voxel-wide image: they are two cases of the record now, both bit-identical.

OpenBLAS chooses its kernels by the CPU, and on CPUs with AVX-512 they fuse multiplications and additions, so FSL's own last bits depend on the machine (FSL-64). The records run FSL on the kernels of CPUs without AVX-512, the order the replica follows on every platform. The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output.

## History {#history}

- **2026-10-29**: the version update. The replica follows FSL 6.0.7.23, first translated from 6.0.7.17's source; its standard comparison runs against FSL 6.0.7.23. In the update's third part, the replica follows 6.0.7.23's new matrix arithmetic.
- **2026-10-30**: the clean room's `bet2` and `bet`.
- **2026-10-31**: the clean room's `betsurf`; the correctly rounded `tanh` on request (`--tanh correctly-rounded`), decided that day ([GLIBC-06](repo:docs/findings/upstream-defects.md#summary)).
- **2026-11-03**: FAST's class variances corrected by default (FSL-202), which the `-B` examples show.
- **2026-11-04**: the replica runs `bet -S`, `-B`, `-A` and `-A2`, with FSL's `standard_space_roi` and `fslroi` and the three standard images in `larmorx-nc`; its standard comparison has 263 cases since. The clean room's `reproduce` computes `powf` and `exp` exactly as glibc 2.35 does, and no notice names it ([GLIBC-07](repo:docs/findings/upstream-defects.md#summary), decided that day). The replica's short random-testing run of 2,699 calls.
- **2026-11-05**: the clean room runs the variations, every program the script runs its own, with its own `standard_space_roi` and `fslroi`, written from [specs/bet.md](repo:specs/bet.md) §5.3 and [specs/standard_space_roi.md](repo:specs/standard_space_roi.md); its record adds them. Each example of the variations shows it since. The random-testing run of 909 calls of both ports, after it.
