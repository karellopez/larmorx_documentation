---
title: FAST
kicker: Evidence · FSL
lede: >-
  `fast` divides a brain into CSF, grey matter and white matter, with the partial volume of each
  tissue in each voxel and a bias field, and fMRIPrep runs it on every T1w. The replica
  (`larmorx-nc`) gives FSL 6.0.7.23's files, messages and exit status byte for byte in all 59 of
  its compared cases, out of 87, fMRIPrep's own calls among them. The clean room (`larmorx`) is
  within its record's thresholds in 64 of its 65 compared cases, out of 102, and gives FSL's bytes
  in 54 of them, fMRIPrep's three calls among them. By default both correct a class variance that
  loses most of its digits (FSL-202), and on fMRIPrep's call the clean room runs 9 to 11 times as
  fast as FSL on one thread, 47 to 67 times on 14.
description: >-
  How LARMORX's two ports of FSL's FAST, a replica and a clean room, compare with FSL 6.0.7.23:
  fMRIPrep's tissue segmentation of three real T1w brains (an adult, a 3.5-year-old, a glioma
  patient) with every file FAST writes, FSL as built and with correctly rounded maths, the tissue
  volumes and fMRIPrep's own outputs, the bias field, FSL's tissue priors with a correction by
  default, a three-channel segmentation, every case of both records with its verdict, random
  testing and the speed.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx-nc</code> <span class="port-licence">FSL Licence: non-commercial use only</span>: translated from FSL 6.0.7.23's source (fsl-fast4 2111.3); it runs as a separate program</li>
<li class="port port--clean-room"><span class="port-name">clean room</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: crate <code>larmorx-fsl</code>, written from <a href="{{ repo('specs/fast.md') }}">specs/fast.md</a>, the FAST paper and runs of FSL 6.0.7.23, without FSL's source (2026-11-03; brought up to the specification's answers on 2026-11-05)</li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--experimental">experimental</span>; clean room <span class="status-tag status-tag--experimental">experimental</span></dd>
<dt>Records</dt><dd>the replica's: <a href="{{ repo('docs/validation/fsl-fast-replica.md') }}">standard comparison</a> (FSL 6.0.7.23) · the clean room's: <a href="{{ repo('docs/validation/fsl-fast.md') }}">standard comparison</a> (FSL 6.0.7.23) · benchmark <a href="{{ repo('docs/benchmarks/fsl-fast.md') }}">fsl-fast</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/fsl-fast.md') }}">fsl-fast</a></dd>
</dl>

## What is compared {#what-it-is}

FAST models the intensities of a skull-stripped brain as a mixture of tissue classes, each a Gaussian: three by default, CSF, grey matter and white matter, in the order of their intensity on a T1w. It finds the class of every voxel by expectation-maximisation, with a hidden Markov random field that favours neighbours of the same class. It starts from a k-means of the brain's intensities, or from given intensities (`-s`), or from FSL's tissue priors registered onto the image (`-a`). It estimates a smooth multiplicative bias field along with the classes and divides it out at each iteration. It ends with the partial volume of each tissue in each voxel: the fraction of CSF, grey and white matter that a voxel at a boundary holds, from a second random field over the mixtures of neighbouring classes.

Its outputs are the segmentation (`_seg`), the partial-volume maps (`_pve_0` to `_pve_2`) and their segmentation (`_pveseg`), and the mixel types. On request it also writes each class's posterior probability (`-p`), its binary image (`-g`), the bias field (`-b`) and the corrected image (`-B`). With `-S n` it segments several registered images together.

fMRIPrep calls it once per subject, in its anatomical workflow (`anat_fit_wf/fast`), on the T1w its brain extraction made (denoised, N4-corrected and skull-stripped): `fast -I 0 -N -p -g -S 1 <T1w brain>`, without a bias field, as N4 corrected it before. Its partial-volume maps become the CSF, grey- and white-matter probability maps fMRIPrep writes (`label-CSF_probseg` and the others), from which its CompCor masks are made.

The two ports run beside FSL 6.0.7.23's `fast` on the same files with the same arguments. fMRIPrep's own outputs are the files it wrote in its run, with FSL in fMRIPrep 25.2.6's image.

```bash
larmorx fsl fast -I 0 -N -p -g -S 1 T1w_brain.nii.gz
larmorx fsl fast -b -B -o out T1w_brain.nii.gz
larmorx fsl fast -S 2 -B -o out T2w_brain.nii.gz T1w_brain.nii.gz
```

The first is fMRIPrep's call. The second also writes the bias field and the corrected image. The third segments two channels; channel 1 is the image named last.

```python
import larmorx as lx

r = lx.fsl.fast("T1w_brain.nii.gz", bias_iterations=0, no_bias=True, probabilities=True,
                segments=True)
csf, gm, wm = r.partial_volumes   # lx.Image each, on the input's grid
labels = r.segmentation.data      # 1 CSF, 2 grey matter, 3 white matter, 0 outside the brain
```

The calls above leave `implementation` at `"auto"`. The [API page](repo:docs/api/fsl-fast.md) describes every option. How to read what follows: [how to read the evidence](/validation/#reading).

### Its two ports {#ports}

FSL comes under the FSL Licence, which allows non-commercial use only. So LARMORX has two ports of its FSL programs. The replica is translated from FSL's source and lives in its own package, `larmorx-nc` (`pip install larmorx-nc`). The clean room is in `larmorx` itself. It is written without FSL's code, from FAST's behavioural specification ([specs/fast.md](repo:specs/fast.md)), the paper (Zhang, Brady and Smith, IEEE TMI 2001) and runs of FSL's program as a black box.

`implementation="auto" | "replica" | "clean-room"` chooses between them (`"original"` in 0.1.0rc1). On the command line, `larmorx --implementation clean-room fsl fast ...` does the same from the next release; in 0.1.0rc1 it is the environment variable `LARMORX_IMPLEMENTATION`. `auto`, and `larmorx fsl fast`, take the replica when `larmorx-nc` is installed, else the clean room.

The replica follows FSL 6.0.7.23. It runs none of FSL's programs and needs no FSL installation: with `-a` it registers the priors with FLIRT's replica, in the same process. Its FSL libraries are the ones the replicas of mcflirt, BET and FLIRT in `larmorx-nc` use too: newimage, the C library's random numbers and maths as FSL's build calls them, and for several channels Armadillo 14.2.1's matrix arithmetic on OpenBLAS's LAPACK.

The clean room has every option, message, exit status and failure case. It segments one channel or any number of them, `-S 9` and more too, which the replica refuses. It registers the tissue priors with FLIRT's clean room in the same process. By default it computes `exp` and `log` correctly rounded on every platform, and in `reproduce` as glibc 2.35 computes them (below). It is built for speed:

- the random field's sweeps keep FAST's in-place order and run as a pipeline of planes, which gives the one-thread result bit for bit at any thread count;
- FSL's blocked sums run block by block in parallel, in their order;
- the partial volumes' 3 + 3 × 101 likelihoods per voxel go through a batched `exp` with the scalar function's bits ([speed](#speed)).

**The C library's last digits (since 2026-11-04).** FSL takes `exp` and `log` from glibc, the C library of Linux, whose results are now and then one unit in the last place away from the exact value rounded once. LARMORX computes them correctly rounded, the same on every platform. Until 2026-11-04 the clean room did so in `fix` and in `reproduce`, so it gave what FSL computes with correctly rounded maths (*identical with correctly rounded maths*) rather than FSL's own bits. Since then its `reproduce` computes them exactly as glibc 2.35 does, with LARMORX's versions of glibc's functions (`larmorx_core::math`). On fMRIPrep's three calls and on every single-channel case of its record it now gives FSL's files bit for bit: 36 cases moved from *identical with correctly rounded maths* to *bit-identical*. Its default, `fix`, still computes these functions correctly rounded; until the catch-up of 2026-11-05 it gave, bit for bit, what FSL computes with correctly rounded maths. That is a *deliberate correction*, GLIBC-07 in the [register](repo:docs/findings/upstream-defects.md), and FAST names it nowhere: whether a segmentation moved with such last bits cannot be told without running it twice (a decision of the project of 2026-11-04, recorded with GLIBC-07).

**The clean-room catch-up (2026-11-05).** The specification's answers of 2026-11-03 ([specs/fast.md](repo:specs/fast.md) §12) are now in the clean room, and every example below was run again with it.

- Its default corrects FSL-202 and FSL-203 and names them, as the replica's default does. FSL-202: with one channel, each class's variance in the logarithm of the intensities subtracts the square of the double-precision mean, where FAST's single-precision square cancels most digits. FSL-203: in an image whose first voxel is NaN, the intensity extrema are taken over the values that are numbers. Its `reproduce` gives FSL's results.
- The record holds the default to the replica's default. With glibc's `exp`, `log`, `expf` and `logf` in the default in place of the correctly rounded ones, the two defaults give the same bits on every single-channel case of the suite. So the examples' comparison *clean room, fix − replica, fix* is the correctly rounded functions' last bits alone: no larger than FSL's own last-bit band, but on the three channels, where it is just beyond it (976 partial-volume values against FSL's 973).
- Also from the answers: `_restore` stays NaN at NaN voxels unless FAST's rule for negative values ran; the lines FAST writes before an abort, as its C library buffers them; a class without weight in several channels (FSL's `MEAN -nan` lines, a permanent case).
- The record gained 13 cases of the clean room's own (`original/`: standard output at FAST's aborts and before the images are read, the NaN voxels of `_restore`), every one within the thresholds or rejected by both alike.

## The verdicts at a glance {#verdicts}

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes: every file FAST writes (each image's header and data), its standard output and error, and its exit status.

{{ ev.agreement('fsl-fast', 'replica') }}

The replica's record runs 87 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-fast-replica.md)). 59 give FSL's files byte for byte. In 27 FSL refuses the input or stops, and the replica does the same, with the same message and exit status (*rejected by both*). Since 2026-11-03 one of them is an image whose first voxel is NaN, where FAST stops with exit status 255 and the replica's default segments it (FSL-203). In one FSL reads and writes past the smaller of two channels of different sizes, which the replica refuses (*expected divergence*: FSL-104). The cases cover:

- fMRIPrep's call on three fMRIPrep runs (an adult, the data panel's 3.5-year-old and its glioma patient), whose partial-volume maps are fMRIPrep's own too;
- every option with its short and long name: the image types, two to four classes and one, the bias field's iterations and smoothing, the random field's weights, `--nopve`, the outputs, `-s`;
- FSL's tissue priors (`-a`, `-A`, `-P`), registered by FLIRT's replica;
- one to eight channels (`-S 2` to `-S 8`: Armadillo's and OpenBLAS's arithmetic followed to 8 × 8 covariances);
- 2D and 4D images, integer images, NaN, negative and very large values;
- every message, exit status and failure case of the command line.

Each case also runs the replica's default, `fix`, where LARMORX corrects FSL's deterministic defects and names them ([below](#corrections)). Since 2026-11-03 that includes the single-channel variance (FSL-202), so the default's outputs of every single-channel case differ from FSL's, by the amounts the examples show.

The replica's random-testing run, half an hour long, drew 17,497 random calls on brain-extracted phantoms and crops of a real T1w: every option, one to four channels, FSL's priors with a drawn matrix. 16,768 agree and 725 are rejected by both alike. 4 differed, all where FLIRT cannot write the registered priors and FAST then uses priors it never allocated (FSL-101): the replica's `reproduce` now stops, or runs on, as FAST does, and the three kinds are cases of the record.

The clean room is written without FSL's source, so its record holds it to the thresholds of [specs/fast.md](repo:specs/fast.md) §11 instead:

- FSL's exit status, files and messages, the numbers in them to 4 significant digits;
- for each class, a Dice coefficient of at least 0.999, with 99.9 % of the brain's voxels identical;
- the partial volumes within 0.001 on average and 0.02 at the 99.9th percentile;
- the bias field within 10⁻⁴.

It also shows how close the clean room comes: each case it passes is classified against FSL as built and against the same unmodified FSL with CORE-MATH's correctly rounded `exp`, `log`, `expf` and `logf` preloaded, whose difference from FSL as built is FSL's own last-bit band.

{{ ev.agreement('fsl-fast', 'original') }}

The clean room's record runs 102 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-fast.md), made again on 2026-11-05). 64 are within the thresholds, 35 are rejected by both alike (the same message and exit status), and 2 are expected divergences: refused where FSL reads past the smaller of two channels (FSL-104), and both defaults correcting FSL-98's cycle of classes, a path FSL never runs. 1 is outside the thresholds.

- **Bit-identical, 54 of the 64.** fMRIPrep's three calls and every single-channel case give FSL's values bit for bit. Until 2026-11-04, 36 of them gave what FSL computes with correctly rounded maths (*identical with correctly rounded maths*), their differences from FSL as built coming from glibc's last bits alone, which `reproduce` now computes as glibc does.
- **Within FSL's own band, 9.** Several channels: the clean room equals FSL as built but in a few partial volumes, each one fraction step of 0.01 away. These are near ties, most likely decided by the last bits of the matrix arithmetic, which the clean room computes with its own LU decomposition: only the cases with several channels show them.
- **Open, 1 more.** `multi/s2-options` has 20 such partial-volume values, 3 of them in an image where FSL's band has 1.
- **Outside the thresholds, 1.** `multi/s5` has five channels, of which the first is nearly a combination of the last two. Each class's 5 × 5 covariance is then nearly singular, and the result is decided by the matrix arithmetic's last bits: the clean room against itself, with one rounding changed, moves further than it lands from FSL. Following LAPACK's operation order is the replica's job.

`opt/nan-first`, an image whose first voxel is NaN (FSL-203), is rejected by both alike since the catch-up: `reproduce` stops as FAST does, and the default segments it, naming FSL-203.

The clean room's first random-testing run, 25 minutes long, drew 9,005 random calls from the same realistic inputs and options as the replica's runs, FSL's runs going through the cache of the original's runs. 8,823 agree. Of the 182 that differed:

- 153 came from the suite's own image reader (FSL's zstd outputs, a NIfTI-2 quaternion), 13 from a NaN bias field outside the brain mask and 12 from messages: all corrected, in the clean room or in the suite, and kept as four permanent cases of the record;
- 3 are explained: two noise-free channels, whose ill-conditioned covariances move with the matrix arithmetic's last bits; and a rank-deficient covariance, where the clean room's LU decomposition finds an exactly zero pivot and aborts, as FAST does on a singular matrix, while FSL's rounding leaves a tiny pivot and it finishes;
- one message stayed open, and is FSL's since the catch-up: a degenerate class whose mean FSL prints as `-nan` and the clean room as 1, the images agreeing ([below](#random)).

## In fMRIPrep: the tissue segmentation of a T1w brain {#example}

fMRIPrep's own call on one of its runs, given to FSL 6.0.7.23 (as built, and with correctly rounded maths), to the replica in `reproduce` and in `fix` (and at one thread), and to the clean room in `reproduce` and in `fix` on 14 threads (and on one). Choose the output above the panels: the segmentation, the three partial-volume maps fMRIPrep keeps, the posterior probabilities, the mixel types, the binary classes.

The replica's differences from FSL are zero in every one, and since 2026-11-04 so are the clean room's in `reproduce`, which computes `exp` and `log` as glibc does. Until then the clean room differed from FSL in a few values, FSL's own last bits, and was FSL with correctly rounded maths bit for bit.

The replica's default, `fix`, differs from FSL since 2026-11-03. It takes each class's variance without FAST's cancellation (FSL-202, a *deliberate correction*), which moves 54 voxels of the segmentation and 112 of the mixel types on this call (the comparison *replica, fix − reproduce*). Measured on seven cases, fMRIPrep's three calls among them, the corrected variance's segmentation and mixel types lie 0 or 1 voxel from FAST computed with its class statistics in double precision throughout, where FSL's lie 1 to 844 voxels from it. Its own last-bit band is 0 voxels, where FSL's reaches 3 to 807: most of FSL's own band, the yardstick's included, is this cancellation.

Until the catch-up the clean room's default gave, bit for bit, what FSL computes with correctly rounded maths. Since 2026-11-05 it makes the replica's correction too. With the C library's functions correctly rounded, it differs from the replica's default in 27, 37 and 10 values of the CSF, grey- and white-matter maps, by at most 0.01, and in no output further than FSL itself moves with those last bits (the comparison *clean room, fix − replica, fix*). Below the viewer, every file FAST writes and the tissue volumes the maps give, with fMRIPrep's own outputs (FSL in fMRIPrep's image).

{{ ev.example('fsl-fast', 'fmriprep-fast') }}

## The bias field {#bias}

FAST's default, which fMRIPrep's call turns off: the bias field estimated along with the classes, in the logarithm of the intensities (where a multiplicative field adds), from each voxel's residual against the class means weighted by its posteriors, smoothed by a Gaussian (its extent `-l`, 20 mm by default), and removed at each iteration. Here it is the record's case `opt/bias-outputs`, on the same T1w at half resolution. Choose the bias field or the corrected image above the panels.

The clean room's bias field is FSL's bit for bit in `reproduce`: its kernel's normalised taps stay in double precision, as runs of FSL showed. Until the catch-up its default gave FSL's with correctly rounded maths bit for bit. Since then it corrects FSL-202 as the replica's default does, and the two defaults differ only by the correctly rounded functions' last bits, within FSL's own band.

{{ ev.example('fsl-fast', 'bias-field') }}

## FSL's tissue priors (-a), and a correction by default {#priors}

With `-a` and a standard-to-input matrix, FAST brings FSL's tissue priors (avg152T1's CSF, grey- and white-matter maps) onto the image with FLIRT and starts the segmentation from them. Here it is the record's case `priors/a-verbose`, on MNI152NLin2009cAsym's T1w.

The priors are stored as 8-bit integers, and FLIRT writes its resampled values in that type truncated toward zero. The replica's default rounds them (FSL-09), so it starts from slightly different priors and its result differs from FSL's, which its `reproduce` gives byte for byte. Since 2026-11-03 the default also corrects the variance (FSL-202), as on every single-channel call. The comparison *replica, fix − reproduce* shows what the corrections change.

The clean room registers the priors with FLIRT's clean room in the same process. Its `reproduce` gives FSL's result bit for bit (since 2026-11-04; FSL's with correctly rounded maths before). Its default makes the same corrections, and the two defaults give the same values, every one (the comparison *clean room, fix − replica, fix*).

{{ ev.example('fsl-fast', 'priors') }}

## Several channels {#multi}

`-S 3` segments three registered images together, here MNI152NLin2009cAsym's T1w, T2w and BOLD reference (the record's case `multi/s3`): each class a Gaussian in three dimensions with its own 3 × 3 covariance, and a bias field per channel. The last image named, the T1w, is channel 1: it names the outputs and orders the classes.

The clean room computes the covariances' determinants and inverses with its own LU decomposition, not LAPACK's. Its `reproduce` equals FSL as built, and its default equals FSL with correctly rounded maths, but in a few partial volumes one fraction step away, within FSL's own band. No correction by default changes this call (the replica's *fix − reproduce* is zero), so the two defaults differ by the correctly rounded functions' last bits alone: here just beyond FSL's own band, 976 grey-matter values against FSL's 973, an open comparison.

{{ ev.example('fsl-fast', 'multi-channel') }}

## On the data panel: a 3.5-year-old and a glioma patient {#panel}

fMRIPrep's call on two runs of the data panel: a 3.5-year-old's T1w (ds000228: a small head, a child's contrast between grey and white matter) and a glioma patient's (ds005003: a 70 mL oligodendroglioma inside the brain mask; the slices go through it). As data-panel cases beside the first example, they are stored as three full-resolution slices, and the crosshair moves through them.

On both, the clean room's `reproduce` gives FSL's files bit for bit, as on ds000005 above, and its default corrects FSL-202 as the replica's does, the two defaults differing only by the correctly rounded functions' last bits. The replica's default differs from FSL on both by FSL-202's correction of the variance ([above](#example)): 66 voxels of the segmentation and 89 of the mixel types for the child, 392 and 453 for the glioma patient.

{{ ev.example('fsl-fast', 'panel-ds000228-child') }}

{{ ev.example('fsl-fast', 'panel-ds005003-glioma') }}

## Random testing after the catch-up {#random}

The clean-room catch-up's random-testing run (2026-11-05) drew the earlier run's cases again and further, on the clean room with the specification's answers: 19,695 random calls in 30 minutes, each compared as the record compares (`reproduce` with FSL, the default with the replica's default). 19,645 agreed. Each of the 50 that differed is in one category below:

- 39 differ only where the default is held to the replica's default. With glibc's functions in the default they are the replica's bit for bit (*identical with correctly rounded maths*): the two defaults differ by the correctly rounded functions' last bits alone. A 40th of that kind was not measured.
- 4 are a class covariance singular in exact arithmetic, where the matrix arithmetic's last bits decide which program aborts.
- 6 are several channels whose run in `reproduce` itself parts from FSL's: 4 open, for FAST's next clean-room part, and 2 whose noise-free channels make each class's covariance ill-conditioned, explained before the catch-up.

{{ ev.table('fsl-fast', 'trial-catchup') }}

{{ ev.table('fsl-fast', 'trial-catchup-triage') }}

## Every case {#cases}

Each case of the two records, the replica's and the clean room's, both against FSL 6.0.7.23 (a column each), with what it tests, its command line, each port's verdict and the reason. The cases random testing gave each port are its own: three of the replica's, five of the clean room's. Search, filter by category or verdict (or select a segment of a chart above), sort by a column; `#case=<name>` links to one case.

{{ ev.cases('fsl-fast') }}

## Speed {#speed}

FSL's `fast` is single-threaded. On fMRIPrep's call the clean room takes 2.4 to 5.2 s on one thread, 9 to 11 times as fast as FSL, and 0.4 to 0.9 s on 14 threads, 47 to 67 times as fast. The replica, a translation, is 1.4 to 1.9 times as fast as FSL's build ([the report](repo:docs/benchmarks/fsl-fast.md)). These timings are informal: one run each, on a machine running other work beside them; FSL's time is that of its run stored in the cache of the original's runs, not run again. The clean room's results are the same bits at any thread count. Its peak memory on fMRIPrep's call, as the memory test measures it at one thread, is 152 MiB, against FSL's 707.

{{ ev.speed('fsl-fast') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default, `fix`, and warns. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives FSL's behaviour byte for byte, where FSL's behaviour is defined ([register](repo:docs/findings/upstream-defects.md)).

- `-p`'s probability maps outside the brain mask (and everywhere with `--nopve` and priors, or without an initialisation iteration) are memory FAST never writes. The replica writes 0 there in `fix` and in `reproduce` and names it (FSL-96). fMRIPrep's call meets it: FSL's maps held zeros there in its three runs of the record; in two multi-channel cases one file held other values, which the record sets to 0 before comparing.
- With several channels and `-N`, the bias field that `-b` saves and `-B` divides by is never computed: no field, in `fix` and in `reproduce` (FSL-97).
- With several channels, FAST's sort of the classes gives a class another class's covariance and posteriors when the classes move in a cycle (given intensities in a cyclic order, for example): each class keeps its own by default (FSL-98).
- A smoothness that is not a number, a bias smoothing of 0 or less and fewer than one class are refused by default, with the reason (FSL-99); FAST uses them as given or aborts.
- FAST aborts when `FSLDIR` is unset, even without priors: the replica segments (FSL-100).
- When FLIRT cannot register the priors, FAST says they are not used and then crashes on priors it never allocated: the replica segments without them (FSL-101).
- `-a` runs FLIRT through the shell with the names unquoted: the replica passes each name whole (FSL-102).
- The brain mask leaves out the voxels of the image's maximum when it is 2<sup>24</sup> or more: corrected (FSL-103).
- Channels of different sizes, which FAST reads past their ends, are refused in `fix` and in `reproduce` (FSL-104).
- Since 2026-11-03, with the specification's answers to the clean room's questions: with one channel, FAST takes each class's variance in the logarithm of the intensities as the mean of the squares minus the square of a single-precision mean, which cancels most of its digits. The replica's default squares the mean in double precision (FSL-202). It changes the default outputs of fMRIPrep's call, toward the exactly computed statistics, as the examples show.
- Also since 2026-11-03: an image whose first voxel is NaN gives FAST NaN intensity extrema and an empty brain mask, and FAST stops with exit status 255. The replica's default takes the extrema over the values that are numbers and segments it (FSL-203).
- Inside `-a`, FLIRT's replica corrects its own defects too (FSL-09, [above](#priors)).

The clean room makes the same corrections by default, with the same notices (FSL-202 and FSL-203 since 2026-11-05). Its `reproduce` follows FSL where FSL's behaviour is defined: for a NaN `-H`, FAST's estimate of the smoothness; FSL-98's pairing; FSL-101's runs and aborts; FSL-102's split of the names; FSL-104 refused in `fix` and in `reproduce`. Inside `-a`, FLIRT's clean room corrects FSL-09 as the replica does. Its default also computes `exp` and `log` correctly rounded, and its `reproduce` as glibc 2.35 does (GLIBC-07, named nowhere: *The C library's last digits*, [above](#ports)).

## Known limits {#limits}

Both ports are experimental. Each record's standard comparison holds fMRIPrep's calls on three fMRIPrep runs. The full comparisons (fMRIPrep's call on every fMRIPrep run), the data panel's other images and the long random-testing runs come in the final validation phase.

The clean room is held to thresholds, not to FSL's bytes. With several channels its own matrix arithmetic leaves a few partial volumes one fraction step from FSL's, and nearly singular covariances (five channels, the first nearly a combination of the last two) are decided by the arithmetic's last bits. The single-channel variance in the logarithm of the intensities cancels most digits, which makes FSL's own band wide on small classes. Measured since (2026-11-03), it is a defect of FAST, FSL-202, corrected by default in both ports: the clean room's since 2026-11-05, held to the replica's default.

Open from the catch-up's random-testing run: which program aborts on a class covariance singular in exact arithmetic, and several channels whose run in `reproduce` parts from FSL's (four random cases).

More than eight channels (`-S 9` and more): the clean room segments them. The replica refuses them in `fix` and in `reproduce`, with a message: FSL's results there follow OpenBLAS's kernels for larger matrices, which it does not reproduce. With several channels whose covariances turn NaN (an empty class), a NaN can carry other payload bits than FSL's; the values and their NaN-ness are FSL's.

Two behaviours of the multi-channel segmentation are kept as FAST's until they are measured on real T1w and T2w pairs. One is its initialisation, which pairs each channel's classes in the order of that channel's own intensities: channels of opposite contrast can start from empty classes, and FAST then ends with every voxel in one class. The other is its bias field.

The cross-platform checks ([how they work](repo:docs/validation/golden.md)) hold the other five platforms to LARMORX's own Linux output; the clean room's cover fMRIPrep's call, the bias field, two channels, the priors, the defects' switches and a 2D image. The benchmark is informal: one run each, on a shared machine.

## History {#history}

- **2026-11-02**: the replica, translated from FSL 6.0.7.23's source.
- **2026-11-03**: the clean room, written from [specs/fast.md](repo:specs/fast.md), the paper and runs of FSL; its first random-testing run, 9,005 calls in 25 minutes. The specification's answers to its questions the same day (§12): the replica's default corrects FSL-202 and FSL-203 since, and its record of 87 cases.
- **2026-11-04**: the clean room's `reproduce` computes `exp`, `log`, `expf` and `logf` as glibc 2.35 does (GLIBC-07): 36 cases moved from *identical with correctly rounded maths* to *bit-identical*, fMRIPrep's three calls among them.
- **2026-11-05**: the clean-room catch-up. The specification's answers of 2026-11-03 are in the clean room since: its default corrects FSL-202 and FSL-203, held to the replica's default; 13 cases of its own; its record made again, 102 cases; the random-testing run of 19,695 calls.
