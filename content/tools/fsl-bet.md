---
title: BET
kicker: Tools · FSL
lede: >-
  FSL's brain extraction (bet, bet2) and its skull and scalp surfaces (betsurf), as an exact
  replica of FSL's source in the separate larmorx-nc package (the FSL Licence's non-commercial
  terms): FSL 6.0.7.23's since the version update of 2026-10-29, first 6.0.7.17's. It gives
  FSL's files byte for byte in every compared case of both versions, fMRIPrep's own calls
  included. The clean-room original in LARMORX (Apache-2.0) is still to be written,
  from a behavioural specification.
description: LARMORX's exact replica of FSL's BET (bet, bet2, betsurf), validated against FSL 6.0.7.23, FSL 6.0.7.17 and fMRIPrep 25.2.6 — fMRIPrep's skull strip of a real BOLD reference, a real T1w with -R, the skull and scalp surfaces to inspect, a three-year-old's BOLD reference from the data panel, and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-nc</code>, under the FSL Licence's terms, run as a separate program); clean-room original planned (<code>larmorx</code>, Apache-2.0, from <a href="{{ repo('specs/bet.md') }}">specs/bet.md</a>)</dd>
<dt>Status</dt><dd><span class="status-tag eco-fsl">validated</span> (the replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/fsl-bet-replica-full.md') }}">replica, full tier</a> (FSL 6.0.7.17) · <a href="{{ repo('docs/validation/fsl-bet-replica.md') }}">standard tier</a> (FSL 6.0.7.23) · API <a href="{{ repo('docs/api/fsl-bet.md') }}">fsl-bet</a></dd>
</dl>

## What it is

BET finds the brain in a head image: a tessellated sphere (2562 vertices) is placed inside the head at its centre of gravity and deformed, a thousand times over, by three forces at each vertex: one along the surface that keeps the vertices evenly spread, one along the normal that keeps the surface smooth, and one along the normal that follows the intensities found inward, against a threshold between the image's robust minimum and the local maximum (`-f`). The brain is what the surface encloses. `bet` is the script around it, with variations: `-R` repeats the extraction from the brain's own centre, `-F` applies the first volume's mask to a 4D series, `-Z` pads an image that is short in z. `betsurf` then casts intensity profiles along the brain surface's normals through the T1 (and a T2) to find the inner skull, the outer skull and the scalp, and deforms three more surfaces onto them.

fMRIPrep calls it on every BOLD run's reference, `bet <boldref> <boldref>_brain.nii.gz -f 0.20 -m`, niworkflows' first skull strip (`enhance_and_skullstrip_bold_wf`), and, where field maps correct the distortion, once more on the corrected reference (`skullstrip_bold_wf`).

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

FSL is distributed under the FSL Licence, which allows non-commercial use only, so LARMORX keeps its FSL tools in two implementations: the exact replica translated from FSL's source, in the separate package `larmorx-nc` (`pip install larmorx-nc`), and a clean-room original in LARMORX itself, written from a behavioural specification without FSL's code. BET's original is the next step; until it exists, LARMORX runs the replica, as a separate program, and says how to install it when it is missing. The replica follows FSL 6.0.7.23 since the version update of 2026-10-29 (it was translated from 6.0.7.17's source; what changed between the two is in its findings), runs none of FSL's programs and needs no FSL installation; its FSL libraries are those every FSL replica of `larmorx-nc` shares (newimage, NewNifti, meshclass, the C library's maths as FSL's Linux build calls it). `bet -S`, `-B`, `-A` and `-A2`, which run standard_space_roi, FLIRT and FAST, wait for those to be replicated. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('fsl-bet', 'replica') }}

{{ ev.agreement('fsl-bet', 'replica-23') }}

The full-tier record runs 173 cases against FSL 6.0.7.17 (the chart above it); since the version update of 2026-10-29 the standard tier, which every merge runs again, runs 176 against FSL 6.0.7.23 (the chart below it): 159 of the full tier's, and the new cases of 6.0.7.23 (`--binaryMask`, the zstd and bzip2 formats) and of random testing. Each of its cases also runs FSL 6.0.7.17 on the same arguments and says what changed between the two versions, and why: the build string in every image's header, the usage text, the new options and formats, FSL-41's fix (a binary image), and one case where FSL's fill reads memory beyond the volume (FSL-43); nothing else. Wherever FSL writes files, the replica writes the same files byte for byte (images: header and data; meshes as text), with FSL's exit status and messages: fMRIPrep's 29 calls on its twelve oracle runs with BOLD runs (the data panel's included), every option of bet2, bet and betsurf, every storage type and file format FSL reads, synthetic heads with a known brain, real T1w images from a child of 3 years to an adult of 82, at 1.5 T, 3 T and 7 T, a tumour and a stroke (with `-R` too), and `betsurf` on real T1w and T2w images from FLIRT's registrations: 364 files of 364 byte for byte (against FSL 6.0.7.23: 315 of 315). Where FSL refuses the input, so does the replica, with FSL's message (*rejected by both*). Where FSL crashes on what it leaves undefined (a constant image, a mesh file it reads without checks, a surface whose centre is not a number), the default refuses with the reason, and `reproduce` keeps everything FSL defines, fills the rest deterministically and names the defect (*expected divergence*); the four pending variations are expected divergences too. Each case is also run in the default mode, where LARMORX corrects FSL's deterministic defects and names them. NaN and infinite voxels give FSL's NaN bits on every platform (the replica computes them with x86-64's rules, checked with ARM's emulated). Random testing draws bet2's, bet's and betsurf's options on random heads of every stored type and runs them through the same comparison ([how random testing works](repo:docs/validation/difftest.md)): its first trial runs found eight kinds of difference, every one fixed, seven kept as cases of the record (`difftest/...`). The version update's trial against FSL 6.0.7.23 left six, each replayed against both versions: two were the replica's (a mask's fill that starts outside the image, which FSL makes through the image's linear index and so reaches its voxels: FSL-43), two the suite's, one a defect of FSL's own (FSL-63: `bet -R` loses a leading `-e`, through bash's `echo`), and one where FSL's fill reads memory beyond the volume (FSL-43, undefined); six cases of the record keep them. Two of those inputs also meet FSL 6.0.7.23's new matrix arithmetic, which the replica does not follow yet (below). The replica needs no more memory than FSL in any call measured, a real T1w and a 240-volume BOLD series included.

## In fMRIPrep: the BOLD reference's skull strip {#example}

fMRIPrep's own call on one of its oracle runs, given to FSL 6.0.7.17, to fMRIPrep's build of FSL (with newer image libraries) and to the replica, beside the outputs fMRIPrep's node wrote, and to FSL 6.0.7.23 with the replica's run compared with it (each panel names its version; *FSL 6.0.7.23 − FSL 6.0.7.17* is FSL's own step). The masks are drawn over the image they were made from; choose *Brain* above the panels for the extracted brain, and the difference panels for what separates two runs.

{{ ev.example('fsl-bet', 'fmriprep-bet') }}

## A real T1w with `-R` {#t1w}

The anatomical use, with the robust centre estimation: the `bet` script runs bet2, measures the brain's centre of gravity (`fslstats -C`), runs bet2 again from it, and stops when the centre moves less than a voxel. The image is shown only inside the brain masks.

{{ ev.example('fsl-bet', 't1w-robust') }}

## The skull and the scalp: `betsurf` {#betsurf}

`betsurf` with a T2 (the call `bet -A2` makes after its registrations) on a synthetic head, which shows the three surfaces whole: on a real head the scalp would show a face. The full-tier record compares betsurf on real T1w and T2w images as well (a child, an adult of 82, a tumour, a Philips scanner), from FLIRT's registrations, byte for byte; their surfaces are not shown here for the same reason.

{{ ev.example('fsl-bet', 'betsurf-head') }}

## On the data panel: a three-year-old's BOLD reference {#panel}

The data panel's youngest subject (ds000228, aged 3.5: a small head, an oblique field of view), through fMRIPrep's BET call; the record runs the call on every panel run with BOLD runs. As a panel case beside the examples above, it is stored as three full-resolution slices; the crosshair moves through them.

{{ ev.example('fsl-bet', 'panel-ds000228-child') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, its verdict and the reason. Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('fsl-bet') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default and warns, with `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) giving FSL's behaviour byte for byte ([register](repo:docs/findings/upstream-defects.md)). Among them: bet2 removes `.hdr` from a name wherever it stands (FSL-40); a mask's fill can start outside the image (FSL-43: on a single slice; FSL then reaches the image's voxels through its linear index, and memory beyond it); the `bet` script splits names with blanks (FSL-44), leaves `-Z`'s outputs padded when FSL is not on the `PATH` (FSL-45), removes files it did not create (FSL-46) and, with `-R`, loses a leading `-e` through bash's `echo` (FSL-63); one skull profile with an empty search range ends betsurf without a message or an output (FSL-50); `--t1only` exits 0 when it fails (FSL-54); an image with two or more extensions gets a wrong data offset (FSL-56); since FSL 6.0.7.23, a name holding `.img` or `.hdr` opens another file (FSL-60) and `--ct` with `--binaryMask` converts the mask instead of the image (FSL-62). Inputs that make no sense, which FSL uses silently, are refused by default with a message naming the entry: NaN or meaningless numeric options (FSL-42), a T2 on another grid (FSL-48), a short matrix file (FSL-53), NaN inside the brain (FSL-55), and since FSL 6.0.7.23 a `--binaryMask` on another grid than the input (FSL-61). Where FSL crashes on what it leaves undefined, the default refuses and `reproduce` fills it deterministically, with a warning: the median of an empty list (FSL-41: a constant or binary image; FSL 6.0.7.23 fixed it, taking the robust maximum), mesh values FSL never sets (FSL-52), a fill from a centre that is not a number (FSL-43). Two of FSL's choices are kept and documented (FSL-49, FSL-57).

## Known limits {#limits}

The clean-room original is not written yet: until it is, BET needs `larmorx-nc` and its licence's non-commercial terms. `bet -S`, `-B`, `-A` and `-A2` are pending FSL's standard_space_roi, FLIRT and FAST. fMRIPrep's image has no `dc`, so its own `bet -R` and `-Z` stop there; the T1w example shows no run of it. FSL 6.0.7.23 computes the inverse of its 4 × 4 matrices through LAPACK (Armadillo 14.2.1), where 6.0.7.17 used a closed form: the last bits change, and the replica follows 6.0.7.17's arithmetic there until its own part follows. No case of the records shows it; random testing found it in bet2's `-c` on an image stored neurologically (a slightly different start, 18 of 15,360 voxels) and in `fslstats -C`'s sign of zero under `bet -R` on a one-voxel-wide image. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). There is no benchmark report yet.
