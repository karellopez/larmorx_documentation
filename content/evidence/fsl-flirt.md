---
title: FLIRT
kicker: Evidence · FSL
lede: >-
  `flirt` finds the affine matrix that aligns one image with another, and fMRIPrep uses its
  boundary-based registration to align every BOLD run with its T1w. Both ports also run the ten
  other programs FSL builds with it, from `convert_xfm` to `applyxfm4D`, and its scripts
  `pairreg`, `extracttxt` and `aff2rigid`. The replica (`larmorx-nc`) gives FSL 6.0.7.23's
  matrices, images and printed results byte for byte in all 211 of its compared cases, out of
  305, fMRIPrep's own calls among them. The clean room (`larmorx`) is within its record's
  thresholds in 239 of its 240 compared cases, out of 339, and gives FSL's bytes in 209 of them.
  On fMRIPrep's three calls its matrices are within 0.0113 mm of FSL's at the 95th percentile of
  the brain, and on 14 threads it runs fMRIPrep's call 12 to 14 times as fast as FSL.
description: >-
  How LARMORX's two ports of FSL's FLIRT (flirt, convert_xfm, avscale, the coordinate programs,
  rmsdiff, makerot, midtrans, pointflirt, applyxfm4D and the scripts pairreg, extracttxt and
  aff2rigid), a replica and a clean room, compare with FSL 6.0.7.23: fMRIPrep's boundary-based
  registration of a real BOLD reference with the white-matter boundary it fits, a default 12-dof
  registration, -applyxfm on a raw BOLD series, two data-panel runs, the matrices as text with
  fMRIPrep's own, FSL's own variability beside the clean room's matrices, every case of both
  records with its verdict, random testing and the speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx-nc</code> <span class="port-licence">FSL Licence: non-commercial use only</span>: translated from FSL 6.0.7.23's source (fsl-flirt 2111.4); it runs as a separate program</li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crate <code>larmorx-fsl</code>, on the registration engine it shares with head-motion correction, written from <a href="{{ repo('specs/flirt.md') }}">specs/flirt.md</a>, the FLIRT and BBR papers and runs of FSL 6.0.7.23, without FSL's source</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--experimental">experimental</span>; clean room <span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/fsl-flirt-replica.md') }}">standard comparison</a> (FSL 6.0.7.23) · the clean room's: <a href="{{ repo('docs/validation/fsl-flirt.md') }}">standard comparison</a> (FSL 6.0.7.23) · benchmark <a href="{{ repo('docs/benchmarks/fsl-flirt.md') }}">fsl-flirt</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/fsl-flirt.md') }}">fsl-flirt</a></dd>
</dl>

## What is compared {#what-it-is}

FLIRT finds the affine matrix that best aligns an input image with a reference. A cost function compares the two images under a candidate matrix: the correlation ratio by default; mutual information, normalised correlation, least squares and others on request. A search over rotations on a coarse grid finds the basin. Powell's method then refines it over a pyramid of blurred and subsampled copies, from 8 mm to the images' own resolution, by the steps of a schedule. The boundary-based cost (`-cost bbr`) instead samples the input's intensity on both sides of a white-matter surface, taken from a segmentation of the reference (`-wmseg`), and rewards a contrast across it. fMRIPrep relies on it to put each BOLD run on its T1w. `-applyxfm` applies a given matrix; `convert_xfm` inverts, concatenates and decomposes matrices.

fMRIPrep calls it once per BOLD run, in its boundary-based registration (`bold_reg_wf/fsl_bbr_wf/flt_bbr`), after mri_coreg's initial alignment: `flirt -in <boldref> -ref <T1w brain> -wmseg <white matter> -init <initial matrix> -schedule $FSLDIR/etc/flirtsch/bbr.sch -dof 6 -searchcost bbr -basescale 1`.

The two ports run beside FSL 6.0.7.23's programs on the same files with the same arguments. fMRIPrep's own output is the file it wrote in its run, with FSL in fMRIPrep 25.2.6's image.

```bash
larmorx fsl flirt -in boldref.nii.gz -ref T1w_brain.nii.gz -dof 6 -cost bbr \
    -wmseg wm.nii.gz -init init.mat -schedule bbr.sch -omat bold2t1.mat -out bold_in_t1
larmorx fsl convert_xfm -omat t12bold.mat -inverse bold2t1.mat
larmorx fsl avscale --allparams bold2t1.mat boldref.nii.gz
larmorx fsl rmsdiff bold2t1.mat other.mat boldref.nii.gz
```

`avscale` prints the matrix's rotations, scales and skews; `rmsdiff` the RMS deviation between two matrices, in mm.

```python
import larmorx as lx

r = lx.fsl.flirt("boldref.nii.gz", "T1w_brain.nii.gz", init="init.mat", cost="bbr",
                 search_cost="bbr", dof=6, base_scale=1, schedule="bbr.sch",
                 wm_seg="wm_mask.nii.gz")
r.matrix          # the 4 × 4 matrix, as -omat writes it
r.image           # the BOLD reference on the T1w's grid
```

The calls above leave `implementation` at `"auto"`. The [API page](repo:docs/api/fsl-flirt.md) describes every program and option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

FSL comes under the FSL Licence, which allows non-commercial use only. So LARMORX has two ports of its FSL programs. The replica is translated from FSL's source and lives in its own package, `larmorx-nc` (`pip install larmorx-nc`). The clean room is in `larmorx` itself. It is written without FSL's code, from a description of what the programs do ([specs/flirt.md](repo:specs/flirt.md)), the papers (Jenkinson and Smith 2001; Jenkinson et al. 2002; Greve and Fischl 2009) and runs of FSL's programs as black boxes.

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). On the command line, `larmorx --implementation clean-room fsl flirt ...` does the same from the next release; in 0.1.0rc1 it is the environment variable `LARMORX_IMPLEMENTATION`. `auto` takes the replica when `larmorx-nc` is installed, else the clean room.

The replica follows FSL 6.0.7.23. It runs none of FSL's programs and needs no FSL installation. Its FSL libraries are the ones the replicas of mcflirt and BET in `larmorx-nc` use too: newimage, its cost functions, and the matrix arithmetic of Armadillo 14.2.1 on OpenBLAS's LAPACK.

The clean room follows FSL 6.0.7.23 too. It has every program, option, message and exit status of the replica. It computes FLIRT's costs, Powell's optimiser and its matrix algebra on the engine that LARMORX's head-motion correction uses ([lx.mri.hmc](/evidence/mri-hmc/)), so the two share one piece of code for the correlation ratio and Woods' cost. It is built for speed. The boundary points, the correlation ratio's bins and the search's grid run in parallel and are summed in a fixed order, so the result is the same at any thread count. Its memory peak stays within 10 % of FSL's, plus the interpreter's 8 MiB, on every measured call.

**The C library's last digits (since 2026-11-04).** FLIRT's arithmetic calls the C library for its rotations' sines and cosines (`sinf`, `cosf`), the angles of a matrix (`atan2f`), the Gaussian blurs (`exp`), the windowed sinc's kernel (`sinf`, `cos`) and the mutual information's logarithms (`logf`). FSL takes them from glibc, the C library of Linux, whose results are now and then one unit in the last place away from the exact value rounded once. LARMORX computes them correctly rounded, the same on every platform, and until 2026-11-04 the clean room did so in `fix` and in `reproduce`. Since then its `reproduce` computes them exactly as glibc 2.35 does, with LARMORX's versions of glibc's functions (`larmorx_core::math`), and what moved is large:

- 41 cases of its record that were within the thresholds without FSL's bytes now give FSL's files byte for byte: FLIRT's default registration and those with 6, 7 and 9 degrees of freedom, mutual information and `normmi`, the windowed sinc, the schedules, the verbose levels up to 3;
- `-cost normmi` and weighted `normmi` pass, 10 mm off before;
- fMRIPrep's three boundary-based calls came closer to FSL's matrices: at the 95th percentile of the brain from 0.0101, 0.0011 and 0.006 mm to 0.0065, 0.0002 and under 0.00001 mm, each then within FSL's own variability (ds005040's is 0.0113 mm since the clean-room catch-up of 2026-11-05, when the clean room took in the specification's answers of 2026-11-03: [the verdicts](#verdicts), [History](#history));
- a registration is an iterative fit, so a few other cases moved the other way, by the size of the fit's own sensitivity to those last bits and within their thresholds: `bbr/default` from 0.020 to 0.069 mm of its 0.1 mm, `real/searchr` from 0.033 to 0.135 mm and `real/weights` from 0.21 to 0.31 mm of their 0.5 mm. The clean room's own two modes part by as much ([findings](repo:docs/findings/fsl-flirt-clean-room.md)).

Its default, `fix`, still computes these functions correctly rounded. That is a *deliberate correction*, GLIBC-07 in the [register](repo:docs/findings/upstream-defects.md), and a registration names it nowhere: whether a registration moved with such last bits cannot be told without running it twice (a decision of the project of 2026-11-04, recorded with GLIBC-07). `avscale`, `makerot` and `convert_xfm -fixscaleskew` name it exactly where their printed or written values differ.

## The verdicts at a glance {#verdicts}

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes: every file FSL writes (the matrix as text, the registered image's header and data), its exit status and its messages.

{{ ev.agreement('fsl-flirt', 'replica') }}

The replica's record runs 305 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-flirt-replica.md)). 211 give FSL's files byte for byte. In 87 FSL refuses the input and the replica refuses it alike, with the same message and exit status (*rejected by both*). In 7 FSL crashes or never finishes, where the replica goes on, or stops with the reason, as its register entry says (*expected divergences*: FSL-71, FSL-72, FSL-75, FSL-93, FSL-204). The cases cover:

- fMRIPrep's boundary-based calls on three fMRIPrep runs (a young adult, the data panel's 82-year-old and its three-year-old), whose matrices are also fMRIPrep's own, as text;
- every cost function with and without weights, the degrees of freedom, the search options, every interpolation and output data type;
- every schedule FSL ships, and written ones that use every command of the schedule language, the principal-axes alignment `alignpaxes` and parameter subsets of any weights among them;
- `-applyxfm` and `-applyisoxfm` on 3D and 4D images, the boundary-based options (its types, slope, given coordinates and normals, a field map), the 2D mode, quaternion parameters (`-anglerep quaternion`), the debug volumes (`-debug`) and every error of the command line;
- `convert_xfm` with every option;
- each path of FLIRT's other programs (`avscale`, `img2imgcoord`, `std2imgcoord`, `img2stdcoord`, `rmsdiff`, `makerot`, `midtrans`, `pointflirt`, `applyxfm4D` in every data type and interpolation) and of its scripts (`pairreg`, `extracttxt`, `aff2rigid`): their usage, every option, their printed results and messages.

Each case also runs the replica's default, `fix`, where LARMORX corrects FSL's deterministic defects and names them; on fMRIPrep's calls it changes nothing.

Four random-testing runs of the replica:

- Its first run, 3,945 random calls on small synthetic images, found two kinds of difference, both fixed and kept as cases of the record. The rest were settled next ([findings](repo:docs/findings/fsl-flirt.md)): FSL corrupting its heap on small images, traced to its background value (FSL-75, below), a base-scale quotient FLIRT takes in single precision (fixed), and two defects LARMORX's default had corrected without naming them (named now).
- Two shorter runs of the new paths, 12,376 and 3,274 random calls (quaternions and the other programs), found one missing message, the background value's order of NaN voxels and makerot's notices, all fixed.
- A run of half an hour on part 3's paths, 209,657 random calls (`midtrans`, `pointflirt`, `applyxfm4D`, the schedule's `alignpaxes` and parameter subsets, `extracttxt`), found `applyxfm4D`'s double-precision arithmetic, the order of NaN voxels in its background value, a singular matrix in a cost evaluation and a volume too large to allocate (FLIRT's exceptions), and `extracttxt`'s messages for a range before the first line: all fixed and kept as cases. The sign of NaN results from images with NaN or infinite voxels in `reproduce` is left open ([findings](repo:docs/findings/fsl-flirt.md)).

Every other finding that fits a run's memory budget agrees, in its shrunk and drawn forms.

The clean room is written without FSL's source, so its record holds it to thresholds instead (specs/flirt.md §13):

- exit statuses and messages FSL's, the numbers in them read as numbers;
- every file FSL writes identical;
- a registration's matrix within a displacement of FSL's over the reference's brain: its 95th percentile within 0.1 mm for the boundary-based and 6-dof registrations, 0.5 mm for the others, or within FSL's own variability where the registration is poorly conditioned;
- its image then within a correlation of FSL's.

A case is *bit-identical* when every value it compares is FSL's. It is *within the original's own variability* when the matrix is beyond the fixed threshold but within FSL's own on the same call with its input perturbed by noise of half an intensity unit (for the worked examples, within that variability measured for them). It is *open* when a file only meets its threshold, or misses it.

{{ ev.agreement('fsl-flirt', 'original') }}

The clean room's record runs the replica's standard cases and its own against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-flirt.md)): the verbose levels and `-debug`, and since the clean-room catch-up of 2026-11-05 also the specification's answers and random testing's permanent cases. 239 of its 240 compared cases are within the thresholds, since the record was made again on 2026-11-07 with the weighted correlation's count (below). 89 are rejected by both alike. 10 are expected divergences: FLIRT crashes or never finishes (FSL-71, FSL-72, FSL-75, FSL-93, and `pointflirt` without points: FSL-204), or `midtrans` writes rows of NaN with exit status 0 (FSL-241, found by the catch-up's runs of FSL; the clean room refuses such transforms in `fix` and in `reproduce`).

- **Bit-identical, 209 cases.** Since 2026-11-04 most registrations: FLIRT's default and 6, 7 and 9 degrees of freedom, the correlation ratio, mutual information and `normmi`, the schedules, `-nosearch`, `-init`, the output's sinc interpolation. The verbose levels up to 3, with `-debug`. `-applyxfm` with nearest neighbour, trilinear and windowed-sinc interpolation, and `convert_xfm`. FLIRT's other programs' printed results and files: `avscale`, the coordinate programs, `rmsdiff`, `makerot`, `midtrans`, `pointflirt`, `applyxfm4D` but for its double-precision sinc and its spline kernels' last bits, `pairreg`'s messages, `extracttxt`, `aff2rigid`. The schedules' and the command line's messages.
- **Within the thresholds.** The verbose levels 5 to 7 and level 2 with `-out`: FSL's lines, their numbers those of the clean room's own path; at levels 5 and above each run of cost evaluations is counted as one, their number following the optimiser's path. A registration that is not bit-identical ends a little elsewhere: its costs follow FSL's arithmetic within their last bits, and the optimiser's path then parts (the boundary-based registrations, `-searchrx`, `-bins 64`, the weighted costs).
- **fMRIPrep's three boundary-based calls** are within 0.0113 mm of FSL's matrices at the 95th percentile of the brain. Two are within FSL's own variability. ds005040's 0.0113 mm is just beyond FSL's own 0.0086 mm (*open*; 0.0065 mm before the catch-up): its boundary-based path, whose costs are not FSL's to the last bit, parts elsewhere since a perturbed row keeps its scales (specs/flirt.md §8.1 step 9). The default 12-dof registration is FSL's, byte for byte.
- **The one case it misses** is the `woods` warning's place in the stream: an ill-posed registration, whose matrix is FSL's text.
- **Cases that pass since 2026-11-04.** Weighted `normcorr` (0.508 mm of its 0.5 mm before) passes since 2026-11-07, its matrix and `-cost normcorr`'s FSL's as text: the weighted correlation's count takes each point's weight as the point is visited ([specs/flirt.md](repo:specs/flirt.md) §6.4, the specification's answer of 2026-11-06), where the clean room had added each row's total at the row's end, which rounds otherwise where the weights are fractional. FSL-91's and FSL-92's reproduced runs and a one-voxel input, where every cost is the same, pass since 2026-11-05: FLIRT's search keeps its starting points of equal cost in the order FSL's sort gives them (libstdc++'s `std::sort`, which is not stable), where the clean room had kept the order it found them in. `-cost leastsq` passes since the catch-up (its three-level sums), `-cost normmi` and weighted `normmi` since 2026-11-04. `pointflirt` without points is refused in `fix` and in `reproduce`, naming FSL-204.

The record's findings explain each ([findings](repo:docs/findings/fsl-flirt-clean-room.md)).

Random testing's run of every program, 9,854 realistic random calls in 24 minutes, found 2,712 differences. The kinds that were the clean room's mistakes were fixed, each checked on the run's cases of its kind: the headers of `-applyisoxfm` and of a reference without coordinates, the zstd and bzip2 outputs of integer images, the forms of an unset sform or qform, the messages of BBR without a boundary point, the `-dof 3` messages, the coordinate programs' and avscale's last digits, `convert_xfm -inverse`. One is a defect of FSL's own (FSL-111, below). The registrations whose paths part on random, often ill-posed pairs stay open, with the sinc and spline kernels' last bits.

## In fMRIPrep: the boundary-based registration of a BOLD reference {#example}

fMRIPrep's own call on one of its runs, given to FSL 6.0.7.23, to the replica and to the clean room, each in `reproduce` and in `fix`, and at one thread: both ports' parallel steps give the same values at any thread count. Choose the panels: the T1w (the reference), the white-matter mask drawn over the BOLD reference at the initial alignment and over FSL's result (the boundary the cost aligns the BOLD contrast to), FSL's registered image, the replica's and the clean room's. FSL's result against its initial alignment shows what the registration changed; the replica's differences from FSL are zero.

The clean room's matrix is 0.0113 mm from FSL's at the 95th percentile of the brain: within its record's 0.1 mm, and just beyond FSL's own 0.0086 mm on the same BOLD reference perturbed by noise of half an intensity unit. Its registered image then differs from FSL's in 42.2 % of the voxels (1 − NCC 2.6 × 10⁻⁶), the largest where a voxel at the edge of the BOLD reference's field of view falls inside it for one matrix and outside for the other. Below the viewer, the matrices as the files hold them, and the displacement each pair gives over the brain.

{{ ev.example('fsl-flirt', 'fmriprep-bbr') }}

## A default registration {#dof12}

FLIRT without options beyond its inputs: 12 degrees of freedom, the correlation ratio, the search over rotations and the default schedule, registering the same BOLD reference to the T1w at half resolution (the record's case `real/default`). Since 2026-11-04 the clean room's matrix and registered image are FSL's, byte for byte. Its default, `fix`, still computes the C library's functions correctly rounded, and its matrix is 0.033 mm from FSL's at the 95th percentile (the comparison *clean room, fix − reproduce*); FSL's own on a perturbed input is 0.005 mm.

{{ ev.example('fsl-flirt', 'dof12') }}

## `-applyxfm` on a raw BOLD series {#applyxfm}

A given matrix applied to four volumes of the raw BOLD series with windowed-sinc interpolation, onto the T1w's grid (the record's case `real/applyxfm-4d`): the resampling part of FLIRT, with its blur of the input where the output grid is coarser. From the same matrix the clean room's values are FSL's, every one, since 2026-11-04. What the specification had left open was the kernel's `sinf` and `cos`, which its `reproduce` now computes as glibc 2.35 does. Its default, `fix`, computes them correctly rounded and differs in 1.6 % of the values, by at most 2.6 × 10⁻⁷ of the image's range, as the clean room did in both modes before.

{{ ev.example('fsl-flirt', 'applyxfm-4d') }}

## On the data panel: an 82-year-old and a three-year-old {#panel}

fMRIPrep's boundary-based call on two runs of the data panel: the first echo of an 82-year-old's multi-echo BOLD run (ds003592) and a three-year-old's BOLD reference (ds000228, a small head and an oblique field of view). As data-panel cases beside the examples above, they are stored as three full-resolution slices, and the crosshair moves through them. On both, the clean room's matrix is within FSL's own variability: 0.0002 mm against 0.0031 mm, and under 0.00001 mm against 0.091 mm.

{{ ev.example('fsl-flirt', 'panel-ds003592-older') }}

{{ ev.example('fsl-flirt', 'panel-ds000228-child') }}

## FLIRT's other programs {#programs}

FSL builds these programs with FLIRT, each with FSL's command line in `larmorx fsl <program>` and a Python function. `avscale` decomposes a matrix into rotations, translations, scales and skews (and the half transforms). `img2imgcoord`, `std2imgcoord` and `img2stdcoord` map coordinates between images through a matrix. `rmsdiff` gives the RMS deviation between two matrices over a sphere of 80 mm, or the largest and RMS displacement over a mask. `makerot` writes a rotation about an axis through a centre. What they print is FSL's text, character for character, from both ports, in the record's `programs/` cases below and in the probe calls behind them (avscale on 400 random matrices).

```python
import numpy as np

m = np.loadtxt("bold2t1.mat")
d = lx.fsl.avscale(m, "boldref.nii.gz", all_params=True)       # avscale --allparams
xyz = lx.fsl.img2imgcoord([[10, 20, 30]], "boldref.nii.gz", "T1w.nii.gz", xfm=m)
lx.fsl.rmsdiff(m, np.eye(4), "boldref.nii.gz")                   # mm
r = lx.fsl.makerot(30, axis=(1, 2, 3), centre=(4, 5, 6))         # 30 degrees
```

The rest of the programs FSL builds with FLIRT came with the replica's part 3 (History). `midtrans` finds the transform to the "middle" of several transforms of images to one template, a Procrustes average about the template's centre. `pointflirt` finds the affine matrix that maps one set of points onto another in the least-squares sense. `applyxfm4D` resamples every volume of a series through one matrix or one per volume, in the series' own data type: char, short, int, float or double, with double precision where FSL keeps it. FLIRT's scripts: `pairreg` registers two brains refined with their skulls, `extracttxt` prints the lines around a match in a text file, and `aff2rigid` approximates a standard-space matrix by a rigid one that keeps the anterior commissure, the AC-PC line and the mid-sagittal plane.

Their matrices and images are FSL's bit for bit in the replica's record (`midtrans`' and `pointflirt`'s singular-value decompositions follow FSL's own LAPACK word for word). The clean room prints the same text and writes the same files: its fits' matrices within 10⁻⁹ of FSL's (a unit of the printed results' last digit), `applyxfm4D`'s nearest-neighbour and trilinear images bit for bit, its sinc and spline images within their last bits, and `pairreg`'s matrix within the record's displacement threshold.

```python
mid = lx.fsl.midtrans(["A2temp.mat", "B2temp.mat", "C2temp.mat"])    # 4 x 4
aff = lx.fsl.pointflirt(in_points, ref_points)                         # N x 3 each, in mm
lx.fsl.applyxfm4d("bold.nii.gz", "boldref.nii.gz", "out.nii.gz", "mats_dir", interp="spline")
rigid = lx.fsl.aff2rigid("T1w2MNI.mat")
```

## Random testing after the catch-up {#random}

The clean-room catch-up's random-testing run (2026-11-05) drew the earlier runs' cases again and further, on the clean room with the specification's answers: 13,907 random calls of every program in 31 minutes, each compared as the record compares. 12,334 agreed within the thresholds; of the 1,140 differences of the run of 2026-11-02 drawn again, 696 now agree. Each of the 1,560 that differed is in one category below. Most are registrations whose path parts from FSL's on random, often ill-posed pairs, and messages whose number follows that path. In 38 `pairreg` runs FSL corrupts its own heap (FSL-75).

Four classes were the clean room's own: FSL's `Cost minima` line on a one-point grid, `-out`'s negative zeros of a completed sform, `applyxfm4D`'s int32 padding and, found afterwards through BET's random testing, the order of the search's starting points of equal cost, which FSL sorts with `std::sort` (873 of the run's path findings: 755 registrations, 101 `pairreg` runs and 17 message counts). Each was fixed with a permanent case of the record, and each of their findings agrees on replay with the final build. FSL's sub-threshold costs on a test volume without intensity range are a question for the specification.

{{ ev.table('fsl-flirt', 'trial-catchup') }}

{{ ev.table('fsl-flirt', 'trial-catchup-triage') }}

## Every case {#cases}

Each case of the two records, the replica's and the clean room's, both against FSL 6.0.7.23 (a column each), with what it tests, its command line, each port's verdict and the reason. Search, filter by category or verdict (or select a segment of a chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('fsl-flirt') }}

## Speed {#speed}

Wall time of the whole command (reading, registering, writing), one run each, on fMRIPrep's call on the record's three fMRIPrep runs and on the record's real registrations ([benchmark](repo:docs/benchmarks/fsl-flirt.md)). These timings are informal: the machine was running other work beside them, and the clean room was timed at its part 2's third step, before the specification's answers changed its arithmetic. FSL and the replica run on one thread; the clean room on one and on 14, with the same result at any thread count.

The clean room's boundary-based cost computes the boundary points' terms in parallel. It runs fMRIPrep's call 1.2 to 1.3 times as fast as FSL on one thread and 12 to 14 times on 14, and the field map's search 3 times as fast on one thread: it skips the steps that cannot reach the mask. The small correlation-ratio registrations are line searches of a few tens of thousands of points, one evaluation after the other: on one thread at FSL's speed (0.9 to 1 times), 3 to 4 times as fast on 14. SIMD sampling is the next step.

{{ ev.speed('fsl-flirt') }}

## Corrections by default {#corrections}

Where FSL has a deterministic defect, both ports correct it by default, `fix`, and warn, in the same way unless said otherwise below. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives FSL's behaviour: the replica's byte for byte, the clean room's within its record's thresholds ([register](repo:docs/findings/upstream-defects.md)).

- FLIRT ends with exit status 0 after any error past its command line (an image or matrix it cannot read, a matrix of the wrong size, an unknown `-bbrtype`). LARMORX exits 1 with FLIRT's message, and 0 in `reproduce` (FSL-68).
- What FSL leaves undefined LARMORX refuses in `fix` and in `reproduce`, with the reason: a schedule's matrix name it cannot interpret, `setoption bbrstep` below 1, a matrix file with a word that is not a number, `-pedir` without a field map (FSL-70 to FSL-73).
- FSL's background value of a volume 3 voxels wide (a level of FLIRT's pyramid on a small image, or the padding of such an input) comes from a buffer too small for the border it writes. FSL corrupts its heap there, and then aborts, crashes or finishes. LARMORX takes the value over the whole border by default, and with `reproduce` the values that fit FSL's buffer (FSL's result where it finishes); it names FSL-75 in both. A single-voxel volume, which has no border, is refused. The same buffer is corrected in `applyxfm4D` and in mcflirt's replica.
- FLIRT shares with mcflirt the integer outputs' clamping (FSL-09), the treatment of infinite voxels (FSL-14) and the order of NaN voxels in a background value (FSL-22).
- `makerot` divides its axis by the square root of its length, so a rotation about an axis that is not of unit length turns by the angle times that root: corrected by default (FSL-76). An axis or centre of other than three values, which FSL reads past, is refused (FSL-77).
- `midtrans` exits with status 0 after an error of its computation, a singular matrix: exit status 1 by default (FSL-78).
- `applyxfm4D`'s spline interpolation of an integer image keeps the spline's coefficients and values in the image's integer type, a coarser and shifted spline: computed as for a float image by default (FSL-79). With `-3D` and sinc it uses a blackman kernel of width 7 instead of the rectangular kernel of width 9 it asks for: the rectangular kernel by default (FSL-80). Both are named only where the written image changes.
- FSL 6.0.7.23's `aff2rigid` stops with a Python error under NumPy 2 before writing its matrix: the matrix is computed by default (FSL-81), FSL's error with `reproduce`.
- The boundary-based cost's normals are scaled by the reference level's voxel sizes, not the segmentation's (FSL-67). Measured on fMRIPrep's three calls and an anisotropic segmentation, computing them in millimetres moves the results by 0.02 mm or less and brings no gain, so they stay FLIRT's in both modes.
- With `-anglerep quaternion` FLIRT composes the search's starting points, which hold Euler angles, as quaternions, so most of them lose their rotation: composed as Euler angles by default, FLIRT's composition with `reproduce`, named in both (FSL-90).
- A `-refweight` or `-inweight` with no voxel of at least 0.01, and an input or reference of a single voxel, make every cost constant and FLIRT's matrix an artefact of its search: refused by default, FLIRT's run with `reproduce` (FSL-91, FSL-92).
- A voxel size of 0 in a header makes the base scale 0, and FLIRT never finishes: counted as 1 by default, as reading the image counts it, and refused with `reproduce`; `-basescale 0` is refused in both (FSL-93).
- `applyxfm4D` reads an image stored as unsigned bytes as signed ones, so its values 128 to 255 enter the interpolation, the background value and the spline's coefficients as negative numbers (a profile 100, 140 interpolated 0.4 of the way gives 13 instead of 116), while `flirt -applyxfm` reads the same image as stored. The clean room reads it as stored by default and as FSL does with `reproduce`, named where a written value changes (FSL-111, found by its runs of FSL). The replica does the same since 2026-11-03: its default names FSL-111 where the bytes written differ, and its `reproduce` reads as FSL does, without a notice.
- `pointflirt` with two coordinate files that hold no point crashes FSL after its messages. Both ports refuse it in `fix` and in `reproduce` after FSL's lines (FSL-204; the replica since 2026-11-03, the clean room since 2026-11-05).
- `midtrans` given transforms whose values reach beyond double precision in its averages (a scale of 10<sup>200</sup>, a translation of 10<sup>300</sup>) writes rows of NaN, or reports its failed decomposition as a matrix-size error, with exit status 0. The clean room refuses them in `fix` and in `reproduce` (FSL-241, found by its runs of FSL on 2026-11-05).

## Known limits {#limits}

Both ports are experimental. The records' standard comparison holds fMRIPrep's calls on three fMRIPrep runs. Their full comparison (fMRIPrep's 22 calls on every fMRIPrep run with BOLD runs) and the data panel's other images run in the final validation phase.

Both ports have every command-line program and script of FSL's FLIRT package, with two exceptions. The coordinate programs' `-warp`, FNIRT's warp fields, is refused with a message until FSL's warp-field libraries are ported. The scripts `flirt_average` and `epi_reg` are not ported yet: they need FSL's other programs (`fslmaths`, FAST, the field maps). `standard_space_roi`, which needs them too, is the replica's since 2026-11-04 and the clean room's since 2026-11-05, with its cases in BET's records ([BET's evidence](/evidence/fsl-bet/#ssroi)).

With NaN or infinite input voxels in `reproduce`, a NaN result can carry the other sign than FSL's (`nan` against `-nan`): an all-NaN matrix from a schedule that optimises relative to a row, and NaN voxels of `applyxfm4D`'s spline interpolation. The values are NaN in both.

The clean room misses its record's thresholds in 1 case ([above](#verdicts)). Beyond them, these are open: the registrations' paths on random, often ill-posed pairs and the messages whose number follows them, the weighted costs' last bits, FSL's sub-threshold costs on a test volume without intensity range, and the sign of a zero skew under gimbal lock (questions for the specification, [specs/flirt.md](repo:specs/flirt.md) §8.1). Its random testing so far is two runs, of 24 and 31 minutes ([above](#random)); the long runs come in the final validation phase.

The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output, and both ports' programs have their cases.

## History {#history}

- **2026-11-01**: the replica, its parts 1 and 2: `flirt` and `convert_xfm` with every cost function, the boundary-based cost and the schedules, and FLIRT's other programs `avscale`, `img2imgcoord`, `std2imgcoord`, `img2stdcoord`, `rmsdiff` and `makerot`.
- **2026-11-02**: the replica's part 3: `midtrans`, `pointflirt`, `applyxfm4D` in every data type and the scripts `pairreg`, `extracttxt` and `aff2rigid`. The clean room, `flirt` and `convert_xfm`; in its part 2 the same day, FLIRT's other programs, `-debug`, the verbose levels and the speed. Six of the replica's cases came with the specification's answers to the clean room's questions: FSL-90 to FSL-93 and the order of NaN voxels in FLIRT's padding (FSL-22).
- **2026-11-03**: three of the replica's cases came with the answers to the clean room's part 2's questions: `applyxfm4D` on uint8 images, trilinear and with `-3D` spline (FSL-111), and `pointflirt` with two coordinate files that hold no point, where FSL crashes and the replica refuses in `fix` and in `reproduce` (FSL-204). The replica's record of 305 cases. The specification's answers of that day (§14): the windowed sinc and the paths through the C library's single-precision sine, cosine and arctangent in `reproduce`, `-debug`'s lines and volumes, avscale's residuals, `applyxfm4D`'s spline in double precision, `leastsq`'s sums.
- **2026-11-04**: the clean room's `reproduce` computes the C library's functions as glibc 2.35 does: 41 cases give FSL's files since, among them the default registration (its matrix 0.033 mm from FSL's before, FSL's own 0.005 mm) and `-applyxfm`'s sinc. fMRIPrep's three calls came from 0.0101, 0.0011 and 0.006 mm to 0.0065, 0.0002 and under 0.00001 mm.
- **2026-11-05**: the clean-room catch-up. The specification's answers of 2026-11-03 are in the clean room since. `-cost leastsq` passes, the search orders its starting points of equal cost as FSL's sort does, `pointflirt` without points and FSL-241's transforms are refused. ds005040's matrix moved from 0.0065 to 0.0113 mm. The random-testing run of 13,907 calls.
- **2026-11-06**: the specification's answer on the weighted correlation's count (§6.4).
- **2026-11-07**: weighted `normcorr` passes; the clean room's record made again, 339 cases.
