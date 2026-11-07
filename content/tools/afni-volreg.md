---
title: 3dvolreg
kicker: Tools · AFNI
lede: >-
  AFNI's rigid-body registration of a series' volumes to a base volume: the alignment behind
  fMRIPrep's BOLD reference, which is the median of 20 of a run's volumes once 3dvolreg has
  aligned them. An exact replica of AFNI 26.3.05's source in LARMORX, which gives every file
  3dvolreg writes, its messages and its exit status bit for bit in every compared case of its
  record, fMRIPrep's calls included. The clean-room original is the next part.
description: >-
  LARMORX's AFNI 3dvolreg, an exact replica validated against AFNI 26.3.05, AFNI 25.2.09 and fMRIPrep 25.2.6 — fMRIPrep's registration of a real BOLD run's reference volumes with its motion parameters, the BOLD reference fMRIPrep makes from them, a correction by default (AFNI-99: the maximum displacement of a mirrored voxel) on the same volumes stored two ways, and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx</code>, Apache-2.0 with CC BY 4.0's attribution for the Medical College of Wisconsin's code, in <code>pip install larmorx</code>), translated from AFNI 26.3.05's source; clean-room original (<code>larmorx</code>, Apache-2.0): the next part, to be written from <a href="{{ repo('specs/3dvolreg.md') }}">specs/3dvolreg.md</a></dd>
<dt>Status</dt><dd><span class="status-tag eco-afni">validated</span> (replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/afni-volreg-replica.md') }}">afni-volreg-replica</a> (standard tier, AFNI 26.3.05) · API <a href="{{ repo('docs/api/afni-volreg.md') }}">afni-volreg</a></dd>
</dl>

## What it is

3dvolreg moves every volume of a series onto a base volume (the first, by default) with a rigid-body transformation: three rotations and three shifts. For each volume it solves a weighted least-squares problem linearised about the current estimate (the volume against the base and the base's derivatives with respect to the six parameters, weighted by the base's own values), resamples, and repeats until the parameters stop changing. `-twopass` first registers blurred copies, starting from a coarse search over shifts and rotations, and refines from there; the resampling is done by four shears, each a shift of rows, with Fourier, heptic, quintic, cubic, linear or nearest-neighbour interpolation (`-Fourier`, the most accurate, fMRIPrep's; heptic by default), on a volume zero-padded by `-zpad` voxels. Besides the registered series it writes, on request, the parameters (`-1Dfile`, `-dfile`), the matrices (`-1Dmatrix_save`), the maximum displacement of a brain voxel per volume (`-maxdisp1D`) and fields of displacements (`-savedisp`); it can apply saved matrices, shift each slice in time first (`-tshift`), and register to another dataset's grid or motion (`-gridparent`, `-rotparent`).

fMRIPrep calls it for every BOLD reference: niworkflows' RobustAverage (the `gen_avg` node of `hmc_boldref_wf`) takes 20 of a run's volumes (on ds000005's first run, volumes 20 to 39 of 240), clips them, divides them by the global signal's drift, gives them to 3dvolreg with `-Fourier -twopass -zpad 4`, and takes the median of the registered volumes as the run's reference; sdcflows' PEPOLAR estimator makes its reference averages the same way.

```bash
larmorx afni 3dvolreg -Fourier -twopass -zpad 4 -prefix registered.nii.gz \
    -1Dfile motion.1D -1Dmatrix_save motion.aff12.1D -maxdisp1D md.1D sliced.nii.gz
```

```python
import larmorx as lx

r = lx.afni.volreg("sliced.nii.gz", **lx.afni.fmriprep_volreg_options())
r.registered, r.parameters, r.matrices, r.max_displacement
```

3dvolreg's results depend on AFNI library routines copyrighted by the Medical College of Wisconsin, which AFNI 26.3.05 releases under CC BY 4.0, so the exact replica is part of LARMORX itself (`pip install larmorx`), under the Apache License with CC BY 4.0's attribution ([NOTICE](repo:NOTICE), [licensing](repo:docs/licensing.md)), and runs in the same process. `implementation="auto"` (and `larmorx afni 3dvolreg`) runs the replica until the clean-room original exists. The replica follows AFNI's arithmetic step by step; AFNI's 3dvolreg has no parallel loop on this path, and neither has the replica, so its results do not depend on the thread count. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

The replica is a translation of AFNI's source, so the question for it is whether it gives AFNI's bytes: the registered series (header and data), every text file 3dvolreg writes, its standard output and error, and its exit status.

{{ ev.agreement('afni-volreg', 'replica') }}

The record runs 190 cases against AFNI 26.3.05 ([the record](repo:docs/validation/afni-volreg-replica.md)). In each of the 137 that write outputs the replica gives AFNI's bytes, every file: the registered series (header and data) and every text file (`-1Dfile`, `-dfile`, `-1Dmatrix_save`, `-maxdisp1D`, `-savedisp`'s datasets). In 21 more neither program writes an output (an existing output, a name with a blank, a directory that does not exist) and both give the same exit status and messages, and in 30 AFNI refuses the input and the replica does the same, with AFNI's message and exit status. Seven of those are AFNI crashing (an option given last without its value, a base whose least squares cannot be set up, a name of 256 bytes, a Fourier rotation that clears a row through a null pointer): there the replica prints AFNI's messages up to the crash and stops with an error instead, an *expected divergence*, as are the two cases where AFNI writes its own dataset format, which LARMORX does not write. The messages are AFNI's, byte for byte, in all 180 cases that run both programs; fMRIPrep's own outputs of its eight calls (RobustAverage's BOLD reference of six BOLD runs from five oracle runs, sdcflows' two PEPOLAR averages) are the replica's, every value, and so are fMRIPrep's build of AFNI's; AFNI 25.2.09 gives 26.3.05's result in all 189 cases it runs (3dvolreg did not change between the two releases); and the Python API gives the command line's outputs in 21 of 21 cases. The cases cover every interpolation method and `-final`, `-twopass` with its options and coarse searches (the subsampled search of a volume of 120 or more voxels along every axis included), the bases, weights, edging and clipping, `-tshift`, `-rotparent`, `-gridparent` and `-twodup`, every output and data type, oblique and sagittal series, NaN, constant and single volumes, the environment's settings, every message, exit status and failure case of the command line, and seven cases from random testing (six from its trial, one from the final build's check). Each case also runs the replica's default mode, where LARMORX corrects AFNI's deterministic defects and names them (below).

## In fMRIPrep: a real run's reference volumes {#example}

fMRIPrep's own call on its oracle run of OpenNeuro ds000005 sub-01, given to AFNI 26.3.05, to AFNI 25.2.09, to fMRIPrep's build of AFNI and to the replica. fMRIPrep keeps only the median of the registered volumes (the next example), so the registered series below is what each program writes for that call; the input panels show the run as stored and the volumes 3dvolreg is given. The charts below the viewer are the motion parameters and maximum displacements, volume by volume.

{{ ev.example('afni-volreg', 'fmriprep-volreg') }}

## The BOLD reference fMRIPrep makes from them {#boldref}

{{ ev.example('afni-volreg', 'fmriprep-boldref') }}

## A correction by default: AFNI-99 {#afni99}

`-maxdisp1D` reports, for each volume, the largest displacement of a voxel inside the base's brain mask, a measure of how much the head moved. AFNI converts the registration's rotation and shift to the dataset's axes with each axis's sign, but takes the voxels' positions without it, so along an axis stored from left to right, posterior to anterior or superior to inferior, it computes the displacement of the voxel mirrored about the axis's centre ([AFNI-99](repo:docs/api/afni-volreg.md#upstream-defects)). The replica's default computes the displacements of the voxels themselves, and names AFNI-99 where a value it prints or writes changes (the messages show two decimals, `-maxdisp1D` three); its reproduce mode gives AFNI's numbers. Below, the volumes of the first example, stored as fMRIPrep gives them (their second axis posterior to anterior) and stored again with that axis reversed: AFNI's maximum displacements depend on the storage order, the replica's do not. The registered volumes are not affected: fMRIPrep, which uses only them, gets the same reference either way.

{{ ev.example('afni-volreg', 'afni-99') }}

## Speed {#speed}

{{ ev.speed('afni-volreg') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, its verdict and the reason. Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('afni-volreg') }}

## Corrections by default {#corrections}

The replica corrects AFNI's deterministic defects by default and warns, with `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) giving AFNI's behaviour byte for byte where AFNI's is defined ([the API page's table](repo:docs/api/afni-volreg.md#upstream-defects)). `-nocoarserot` turns the coarse rotation search off, as documented (AFNI-86: AFNI reads it as `-noclip`, whose four letters it tests first). A byte series is written with its values rounded (AFNI-87: AFNI stretches them to the full byte range). Output names of 256 bytes or more are written (AFNI-90: AFNI aborts on a buffer overflow; `-maxdisp1D`'s name is cut at 997 bytes). The coarse rotation search's mask always uses its own clip fraction (AFNI-92: `-nomaxdisp` changes it in AFNI), and an empty search region is not taken as the best (AFNI-93). A second `-base` is refused (AFNI-95: AFNI keeps the last). A Fourier rotation that would clear a row through a null pointer clears it (AFNI-97: AFNI crashes). Two messages name the dataset they are about (AFNI-98: AFNI prints `(null)` or a stray argument). The maximum displacements of the voxels themselves (AFNI-99, above). Inputs that make no sense stop with a clear error in both modes: an option given last without its value (AFNI-88), a base on which the least squares cannot be set up (AFNI-89), `-coarse 1` on a volume of 120 or more voxels along every axis (AFNI-94: AFNI loops for ever), a `-rotparent` without its centres (AFNI-96).

## Known limits {#limits}

The record's standard tier holds fMRIPrep's RobustAverage calls on six BOLD runs of five oracle runs (single-band, multiband, multi-echo, uint16 and float32 storage) and sdcflows' two PEPOLAR reference averages; the full tier (seven more of the data panel's runs) and long random testing run in the final validation phase. Sub-brick selectors (`dset[n]`) and AFNI's own `.HEAD/.BRIK` format are refused, as by every LARMORX AFNI tool, and LARMORX writes no AFNI header extension, so a LARMORX output cannot serve as a `-rotparent` (AFNI's can). The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). The speed figures are informal timings; the benchmark report comes with the clean-room original, built for speed.
