---
title: FAST
kicker: Tools · FSL
lede: >-
  FSL's tissue segmentation (fast): the brain divided into CSF, grey matter and white matter with
  a hidden Markov random field, a bias field and the partial volume of each tissue in each voxel,
  the segmentation fMRIPrep runs on every T1w. An exact replica of FSL 6.0.7.23's source in the
  separate larmorx-nc package (the FSL Licence's non-commercial terms), experimental, which gives
  every file FAST writes, its messages and its exit status bit for bit in every compared case of
  its record, fMRIPrep's own calls included. The clean-room original is still to be written.
description: LARMORX's FSL FAST, an exact replica validated against FSL 6.0.7.23 — fMRIPrep's tissue segmentation of three real T1w brains (an adult, a 3.5-year-old, a glioma patient) with every file FAST writes, the tissue volumes and fMRIPrep's own outputs, the bias field, FSL's tissue priors with a correction by default, a three-channel segmentation, and every parity case of the record with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-nc</code>, under the FSL Licence's terms, run as a separate program), translated from FSL 6.0.7.23's source (fsl-fast4 2111.3); clean-room original (<code>larmorx</code>, Apache-2.0): planned, to be written from <a href="{{ repo('specs/fast.md') }}">specs/fast.md</a></dd>
<dt>Status</dt><dd><span class="status-tag status-tag--experimental">experimental</span> (replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/fsl-fast-replica.md') }}">fsl-fast-replica</a> (standard tier, FSL 6.0.7.23) · API <a href="{{ repo('docs/api/fsl-fast.md') }}">fsl-fast</a></dd>
</dl>

## What it is

FAST models the intensities of a skull-stripped brain as a mixture of tissue classes, each a Gaussian (three by default: CSF, grey matter and white matter, in the order of their intensity on a T1w), and finds the class of every voxel by expectation-maximisation with a hidden Markov random field that favours neighbours of the same class. It starts from a k-means of the brain's intensities (or from given intensities, `-s`, or from FSL's tissue priors registered onto the image, `-a`), estimates a smooth multiplicative bias field along with the classes and divides it out at each iteration, and ends with the partial volume of each tissue in each voxel: the fraction of CSF, grey and white matter a voxel at a boundary holds, from a second random field over the mixtures of neighbouring classes. Its outputs: the segmentation (`_seg`), the partial-volume maps (`_pve_0` to `_pve_2`) and their segmentation (`_pveseg`), the mixel types, and on request each class's posterior probability (`-p`), its binary image (`-g`), the bias field (`-b`) and the corrected image (`-B`); with `-S n` it segments several registered images together.

fMRIPrep calls it once per subject, on the T1w its brain extraction made (denoised, N4-corrected and skull-stripped), in its anatomical workflow (`anat_fit_wf/fast`): `fast -I 0 -N -p -g -S 1 <T1w brain>`, without a bias field (N4 corrected it before). Its partial-volume maps become the CSF, grey- and white-matter probability maps fMRIPrep writes (`label-CSF_probseg` and the others), from which its CompCor masks are made.

```bash
larmorx fsl fast -I 0 -N -p -g -S 1 T1w_brain.nii.gz             # fMRIPrep's call
larmorx fsl fast -b -B -o out T1w_brain.nii.gz                   # the bias field and the corrected image
larmorx fsl fast -S 2 -B -o out T2w_brain.nii.gz T1w_brain.nii.gz   # two channels (channel 1 named last)
```

```python
import larmorx as lx

r = lx.fsl.fast("T1w_brain.nii.gz", bias_iterations=0, no_bias=True, probabilities=True,
                segments=True)
csf, gm, wm = r.partial_volumes   # lx.Image each, on the input's grid
labels = r.segmentation.data      # 1 CSF, 2 grey matter, 3 white matter, 0 outside the brain
```

FSL is distributed under the FSL Licence, which allows non-commercial use only, so LARMORX keeps its FSL tools in two implementations: the exact replica translated from FSL's source, in the separate package `larmorx-nc` (`pip install larmorx-nc`), and a clean-room original in LARMORX itself, written from a behavioural specification without FSL's code. For FAST only the replica exists so far: `implementation="auto"` (and `larmorx fsl fast`) runs it when `larmorx-nc` is installed, and a clear error names the package otherwise. The replica follows FSL 6.0.7.23, runs none of FSL's programs and needs no FSL installation (with `-a` it registers the priors with FLIRT's replica, in the same process); its FSL libraries (newimage, the C library's random numbers and maths as FSL's build calls them, Armadillo 14.2.1's matrix arithmetic on OpenBLAS's LAPACK for several channels) are those every FSL replica of `larmorx-nc` shares with mcflirt, BET and FLIRT. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

The replica is a translation of FSL's source, so the question for it is whether it gives FSL's bytes: every file FAST writes (each image's header and data), its standard output and error, and its exit status.

{{ ev.agreement('fsl-fast', 'replica') }}

The record runs 86 cases against FSL 6.0.7.23 ([the record](repo:docs/validation/fsl-fast-replica.md)): 59 give FSL's files byte for byte, in 26 FSL refuses the input or stops and the replica does the same, with the same message and exit status (*rejected by both*), and in one FSL reads and writes past the smaller of two channels of different sizes, which the replica refuses (*expected divergence*: FSL-104). They cover fMRIPrep's call on three oracle runs (an adult, the data panel's 3.5-year-old and its glioma patient; fMRIPrep's own partial-volume maps the same too), every option with its short and long name (the image types, two to four classes and one, the bias field's iterations and smoothing, the random field's weights, `--nopve`, the outputs, `-s`), FSL's tissue priors (`-a`, `-A`, `-P`, registered by FLIRT's replica), one to eight channels (`-S 2` to `-S 8`: Armadillo's and OpenBLAS's arithmetic followed to 8 × 8 covariances), 2D and 4D images, integer images, NaN, negative and very large values, and every message, exit status and failure case of the command line. Each case also runs the replica's default mode, where LARMORX corrects FSL's deterministic defects and names them (below). Random testing's trial (half an hour, 17,497 random calls on brain-extracted phantoms and crops of a real T1w, every option, one to four channels, FSL's priors with a drawn matrix): 16,768 agree, 725 are rejected by both alike, and 4 differed, all where FLIRT cannot write the registered priors and FAST then uses priors it never allocated (FSL-101): the replica's `reproduce` mode now stops, or runs on, as FAST does, and the three kinds are cases of the record.

## In fMRIPrep: the tissue segmentation of a T1w brain {#example}

fMRIPrep's own call on one of its oracle runs, given to FSL 6.0.7.23 and to the replica in its reproduce and default modes (and at one thread). Choose the output above the panels: the segmentation, the three partial-volume maps fMRIPrep keeps, the posterior probabilities, the mixel types, the binary classes; the replica's differences from FSL are zero in every one. Below the viewer, every file FAST writes and the tissue volumes the maps give, with fMRIPrep's own outputs (FSL in fMRIPrep's image).

{{ ev.example('fsl-fast', 'fmriprep-fast') }}

## The bias field {#bias}

FAST's default, which fMRIPrep's call turns off: the bias field estimated along with the classes, in the logarithm of the intensities (where a multiplicative field adds), from each voxel's residual against the class means weighted by its posteriors, smoothed by a Gaussian (its extent `-l`, 20 mm by default), and removed at each iteration (the record's case `opt/bias-outputs`, on the same T1w at half resolution). Choose the bias field or the corrected image above the panels.

{{ ev.example('fsl-fast', 'bias-field') }}

## FSL's tissue priors (-a), and a correction by default {#priors}

With `-a` and a standard-to-input matrix, FAST brings FSL's tissue priors (avg152T1's CSF, grey- and white-matter maps) onto the image with FLIRT and starts the segmentation from them (the record's case `priors/a-verbose`, on MNI152NLin2009cAsym's T1w). The priors are stored as 8-bit integers, and FLIRT writes its resampled values in that type truncated toward zero; the replica's default rounds them (FSL-09), so it starts from slightly other priors and its result differs from FSL's, which its reproduce mode gives byte for byte. The difference *replica, default − reproduce mode* shows what the correction changes.

{{ ev.example('fsl-fast', 'priors') }}

## Several channels {#multi}

`-S 3` segments three registered images together, here MNI152NLin2009cAsym's T1w, T2w and BOLD reference (the record's case `multi/s3`): each class a Gaussian in three dimensions with its own 3 × 3 covariance, a bias field per channel. The last image named, the T1w, is channel 1: it names the outputs and orders the classes.

{{ ev.example('fsl-fast', 'multi-channel') }}

## On the data panel: a 3.5-year-old and a glioma patient {#panel}

fMRIPrep's call on two runs of the data panel: a 3.5-year-old's T1w (ds000228: a small head, a child's contrast between grey and white matter) and a glioma patient's (ds005003: a 70 mL oligodendroglioma inside the brain mask; the slices go through it). As panel cases beside the first example, they are stored as three full-resolution slices; the crosshair moves through them.

{{ ev.example('fsl-fast', 'panel-ds000228-child') }}

{{ ev.example('fsl-fast', 'panel-ds005003-glioma') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, its verdict and the reason. Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('fsl-fast') }}

## Corrections by default {#corrections}

The replica corrects FSL's deterministic defects by default and warns, with `upstream_defects="reproduce"` (`LARMORX_UPSTREAM_DEFECTS=reproduce`) giving FSL's behaviour byte for byte where FSL's is defined ([register](repo:docs/findings/upstream-defects.md)). `-p`'s probability maps outside the brain mask (and everywhere with `--nopve` and priors, or without an initialisation iteration) are memory FAST never writes: the replica writes 0 there in both modes and names it (FSL-96); fMRIPrep's call meets it (FSL's maps held zeros there in its three runs of the record; in two multi-channel cases one file held other values, which the record sets to 0 before comparing). With several channels and `-N`, the bias field `-b` saves and `-B` divides by is never computed: no field in both modes (FSL-97). With several channels, FAST's sort of the classes gives a class another class's covariance and posteriors when the classes move in a cycle (given intensities in a cyclic order, for example): each class keeps its own by default (FSL-98). A smoothness that is not a number, a bias smoothing of 0 or less and fewer than one class are refused by default, with the reason (FSL-99; FAST uses them as given or aborts). FAST aborts when `FSLDIR` is unset, even without priors: the replica segments (FSL-100). When FLIRT cannot register the priors, FAST says they are not used and then crashes on priors it never allocated: the replica segments without them (FSL-101). `-a` runs FLIRT through the shell with the names unquoted: the replica passes each name whole (FSL-102). The brain mask leaves out the voxels of the image's maximum when it is 2^24 or more: corrected (FSL-103). Channels of different sizes, which FAST reads past their ends, are refused in both modes (FSL-104). Inside `-a`, FLIRT's replica corrects its own defects too (FSL-09, above).

## Known limits {#limits}

The replica is experimental. The record's standard tier holds fMRIPrep's calls on three oracle runs; its full tier (fMRIPrep's call on every oracle run) and the data panel's other images run in the final validation phase. More than eight channels (`-S 9` and more) are refused in both modes with a message: FSL's results there follow OpenBLAS's kernels for larger matrices, which the replica does not reproduce. With several channels whose covariances turn NaN (an empty class), a NaN can carry other payload bits than FSL's (the values and their NaN-ness are FSL's). Two behaviours of the multi-channel segmentation are kept as FAST's until they are measured on real T1w and T2w pairs: its initialisation, which pairs each channel's classes in the order of that channel's own intensities (channels of opposite contrast can start from empty classes, and FAST then ends with every voxel in one class), and its bias field. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md). There is no benchmark report yet: speed is measured with the clean-room original.
