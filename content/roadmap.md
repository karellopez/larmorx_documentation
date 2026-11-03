---
title: Roadmap
kicker: Documentation
lede: What LARMORX has completed, what is under way and what comes next, in order. This page is updated whenever a step is completed.
description: The LARMORX roadmap — the step under way, the next steps in order (the newest releases of the originals, the remaining ports from FSL, sdcflows and FreeSurfer, the pipeline), the final validation phase, the first release, and every step completed so far with its date.
evidence: true
wide: true
---

**Last updated: 2026-11-03.** LARMORX advances one step at a time, and each step is finished before the next begins: its code, its tests against the original program, its validation record and its page on this site ([how each step is tested](/validation/#levels)). The working plan behind this page, with every follow-up, is in the repository's [next steps](repo:docs/next-steps.md).

## Under way and next {#next}

| | Step | What it delivers | Status |
|---|---|---|---|
| 1 | **FAST and topup** | FSL's tissue segmentation and field-map estimation, each a replica and a clean-room original | FAST's replica complete (2026-11-02): `fast` with every option, one to eight channels and FSL's tissue priors, 59 of 59 compared cases bit-identical to FSL 6.0.7.23, fMRIPrep's call on three oracle runs included; [its page](/tools/fsl-fast/); FAST's clean-room original complete (2026-11-03): every option, any number of channels, 60 of 61 compared cases within its thresholds, fMRIPrep's call on three oracle runs bit for bit what FSL computes with correctly rounded maths, 9 to 11 times faster than FSL on one thread and 47 to 67 times on 14; topup's replica complete (2026-11-03): `topup` and `applytopup` with every option and method, 104 of 104 compared cases bit-identical to FSL 6.0.7.23, fMRIPrep's call on two oracle runs included; [its page](/tools/fsl-topup/); topup's clean-room original next |
| 2 | **fslmaths and fslstats** | FSL's image arithmetic and statistics, every operation, a replica and a clean-room original each: fMRIPrep calls them in every BOLD reference's skull strip and in the optional goodvoxels mask; then BET's options that need FLIRT, FAST and `fslmaths` (`-S`, `-B`, `-A`, `-A2`) | Planned |
| 3 | **Field maps** | sdcflows' field-map estimation: the B-spline fit, reversed phase encoding (PEPOLAR) and phase difference | Planned |
| 4 | **FreeSurfer 8.2.0** | Every program complete, a replica (`larmorx-freesurfer`) and a clean-room original built for speed: first the reference runs on the [data panel](/data-panel/), then FreeSurfer's shared library, then the programs fMRIPrep runs, slowest first | Planned |
| 5 | **Surfaces** | Surface tools compatible with Connectome Workbench and MSM | Planned |
| 6 | **Confounds** | CompCor, DVARS, framewise displacement and fMRIPrep's other confounds | Planned |
| 7 | **larmorprepx** | The pipeline: BIDS in, fMRIPrep-compatible derivatives and HTML reports out | Planned |

New releases of the originals are followed as they come out: a weekly check lists every newer release and the files it changes, and each update is a step of its own.

## The final validation phase {#final}

Once every tool is ported, the extensive testing runs for every tool at once, and each tool's page grows with it ([levels of testing](/validation/#levels-plan)):

- the full tier and the fourteen datasets of the [data panel](/data-panel/) for every tool, against the newest releases;
- long random-testing runs of several hours for every tool, and every heavy random case run to its end;
- wider studies across thread counts, and speed and memory studies;
- an independent review of every large port;
- then the comparisons with fMRIPrep, stage by stage and end to end, against its newest release.

## The first release {#release}

- A check on clean machines, without compilers or runtimes installed (Windows, a minimal Linux).
- The Windows runtime linked into the programs; smaller binaries.
- A release workflow: the wheels for the six platforms, built, tested and uploaded on a version tag; the package names reserved on PyPI.
- A page explaining why LARMORX is built in Rust with Python on top: why the original tools have no Windows version, what Rust gives and what the project's own rules add (its own maths functions, one fixed order for matrix arithmetic, the same digits on every platform), and the honest limits.

## Completed {#done}

Newest first. The records of every tool are in the repository's [docs/validation](repo:docs/validation/); the decisions behind each step in its [decision log](repo:docs/decision-log.md).

| Completed | Step |
|---|---|
| 2026-11-03 | **topup's replica.** FSL's susceptibility-field estimation and its correction translated from FSL 6.0.7.23's source, with the FSL libraries they need (B-spline fields and their regularisers, sparse matrices, non-linear optimisers, warps): every option, message and failure case of `topup` and `applytopup`, applytopup's undocumented variational methods included; every file both programs write bit for bit in every compared case, fMRIPrep's call on two oracle runs included (fMRIPrep's own outputs the same); FSL-116 to FSL-143 corrected by default (the thread count, the membrane energy's units, the first volume's interpolation, a divergent prior, options without meaning); [the page](/tools/fsl-topup/) |
| 2026-11-03 | **FAST's clean-room original.** FSL's tissue segmentation written in LARMORX itself (Apache-2.0) from its behavioural specification, the paper and black-box runs of FSL's program, without FSL's code: every option, message and failure case, one channel or any number, FSL's tissue priors registered by FLIRT's clean-room original; 60 of 61 compared cases within its thresholds, fMRIPrep's call on three oracle runs bit for bit what FSL computes with correctly rounded maths; built for speed (parallel sweeps with the serial result, a vectorised `exp` with the same bits): 2.4 to 5.2 s on one thread against FSL's 22 to 60 s, under a second on 14; [the page](/tools/fsl-fast/) |
| 2026-11-02 | **FAST's replica.** FSL's tissue segmentation translated from FSL 6.0.7.23's source: the hidden Markov random field, the bias field and the partial volumes, every option, message and failure case, one to eight channels (FSL's matrix arithmetic followed to 8 × 8 covariances) and FSL's tissue priors registered by FLIRT's replica; every file FAST writes bit for bit in every compared case, fMRIPrep's call on three oracle runs included; FSL-96 to FSL-104 corrected by default (memory FAST never writes, the multi-channel class sort, the mask's brightest voxels, meaningless options, FAST's aborts and crashes); [the page](/tools/fsl-fast/) |
| 2026-11-02 | **FLIRT's clean-room original, part 2: FLIRT complete.** FLIRT's other programs (avscale, the coordinate programs, rmsdiff, makerot, midtrans, pointflirt, applyxfm4D) and scripts (pairreg, extracttxt, aff2rigid), `-debug` and every verbose level, written from the specification and black-box runs; the specification's answers to the clean-room original's 20 questions (each checked by a model written from the specification's text alone; the replica gained FSL-90 to FSL-93, 302 cases) closed 22 of its 30 open cases; fMRIPrep's three boundary-based calls within 0.011 mm of FSL's matrices, 12 to 14 times FSL's speed on 14 threads; FSL-111 found (applyxfm4D's 8-bit images read as signed bytes); [the page](/tools/fsl-flirt/) shows it beside FSL and the replica, with FSL's own variability; [the record](repo:docs/validation/fsl-flirt.md): 206 of 214 compared cases within thresholds |
| 2026-11-02 | **FLIRT's clean-room original, part 1.** `flirt` and `convert_xfm` written from the specification alone, on the registration engine of LARMORX's head-motion correction (shared, never copied; its results unchanged): fMRIPrep's three boundary-based calls within 0.1 mm of FSL's, `-applyxfm`'s images FSL's bit for bit, `convert_xfm` and the messages FSL's; 89 of 111 compared cases within thresholds, the others waiting for the specification's answers; fMRIPrep's boundary-based call in 38 s on one thread and 5.9 s on eight (FSL: 46 s) |
| 2026-11-02 | **FLIRT's replica, part 3.** The rest of FSL's FLIRT package: `midtrans`, `pointflirt`, `applyxfm4D` in every data type (double precision included), the scripts `pairreg`, `extracttxt`, `aff2rigid`, the schedule's principal-axes alignment and any parameter subset (FSL's own LAPACK translated word for word), `-debug`; FSL-78 to FSL-81 corrected by default; [the page](/tools/fsl-flirt/) |
| 2026-11-01 | **FLIRT's replica, parts 1 and 2.** `flirt` and `convert_xfm` with every cost function, BBR and the schedules, bit-identical to FSL 6.0.7.23 in every compared case, fMRIPrep's boundary-based calls included; FLIRT's other programs (avscale, img2imgcoord, std2imgcoord, img2stdcoord, rmsdiff, makerot), quaternion parameters, FSL's heap overflow in the background value traced and corrected (FSL-75); [the page](/tools/fsl-flirt/) with fMRIPrep's boundary-based registrations |
| 2026-11-01 | **BET's clean-room original** (`bet`, `bet2`, `betsurf`), written from its behavioural specification and built for speed, beside the exact replica: every `bet2` and `bet` brain, mask and outline of the standard tests bit-identical to FSL 6.0.7.23's (fMRIPrep's calls included), `betsurf`'s profiles decided as FSL's and its masks within their thresholds on 4 of 5 real heads; 2.5 to 3.6 times FSL's speed on one thread, 6.5 to 13.5 times on 24. Open questions for its specification: a centre on neurologically stored images, `betsurf` where few profiles vote and on small images |
| 2026-10-30 | **A cube root with the C library's digits, for `reproduce`.** 3dUnifize `-EPI`, in the clean-room original and the replica, keeps LARMORX's correctly rounded cube root by default (naming GLIBC-05 where the C library's last bit would change the result) and gives AFNI's exact result in `reproduce` mode, through a clean-room cube root with the C library's bits, proved on all 2^32 inputs; with it, mcflirt's replica handles FSL-65 and FSL-66 as the clean-room original does, and the parity tests run in parallel (the same outcome for every test) |
| 2026-10-30 | **Two clean-room additions.** The clean-room head-motion correction now handles mcflirt's FSL-20, FSL-21, FSL-65 and FSL-66 as the specification says (outputs that cannot be written, impossible bin counts), and the clean-room 3dUnifize stops before an impossible `-EPI` neighbourhood (AFNI-75), with the same words as the replica |
| 2026-10-30 | **3dUnifize's replica: memory as AFNI's.** Peak memory within the rule with `-T2` and `-EPI` (it held 1.5 and 2.8 times AFNI's); the specifications of FSL-20, FSL-21, FSL-65, FSL-66, AFNI-75 and a cube root with the C library's exact results written for the clean-room implementers |
| 2026-10-30 | **The AFNI replicas in the main package.** AFNI 26.3.05 releases the Medical College of Wisconsin's code under CC BY 4.0, so the exact replicas of 3dTshift, 3dAutomask and 3dUnifize left the separate GPL package for LARMORX itself (`pip install larmorx`, Apache-2.0 with CC BY 4.0's attribution) and run in its process; the C library's sine and cosine they need come from Arm's MIT routines, proved equal to glibc's on every input; their records, re-made in-process, agree case for case |
| 2026-10-29 | **SciPy, NumPy and OpenBLAS at their newest releases.** The one-shot BOLD resampler follows SciPy 1.18.1 (its fix of the `reflect` boundary, SCI-03) and is checked against numpy 2.5.4 with OpenBLAS 0.3.34 (nothing LARMORX follows changed); the FSL replicas follow FSL 6.0.7.23's matrix library (Armadillo 14.2.1 on OpenBLAS 0.3.33) bit for bit, so mcflirt's 5 expected divergences pass; FSL's own last digits depend on the computer's processor (FSL-64), and every record runs FSL on one set of kernels |
| 2026-10-29 | **The clean-room originals at the newest releases.** 3dTshift, 3dAutomask and 3dUnifize follow AFNI 26.3.05 and the head-motion correction mcflirt 6.0.7.23 (its zstd and bzip2 formats, FSL-59, FSL-60), as their replicas do; the head-motion correction's `-cost mutualinfo` and `normmi` computed exactly, as well aligned as mcflirt's on 169 random phantoms |
| 2026-10-29 | **FSL 6.0.7.23.** The mcflirt and BET replicas follow FSL's newest release (FSL-59 to FSL-63 registered; FSL-41 fixed upstream); every example on their pages shows both releases |
| 2026-10-29 | **AFNI 26.3.05.** The 3dTshift, 3dAutomask and 3dUnifize replicas follow AFNI's newest release; a weekly check for new releases of every original |
| 2026-10-29 | **The clean-room fixes.** 12 of the 13 differences that random testing and the data panel found in the clean-room originals of 3dTshift, 3dAutomask, 3dUnifize and the head-motion correction fixed or explained |
| 2026-10-28 | **antsAI and antsAffineInitializer: memory and speed.** Peak memory at or below ANTs'; antsAI about twice as fast |
| 2026-10-28 | **fMRIPrep's template registrations at full size.** antsRegistration on the fourteen panel runs: 14 of 14 identical to ANTs with correctly rounded maths |
| 2026-10-27 | **The ANTs tools on the data panel.** Every ANTs call of fMRIPrep's fourteen panel runs, and the panel's own images |
| 2026-10-26 | **BET**, the exact replica (`bet`, `bet2`, `betsurf`) |
| 2026-10-25 | **mcflirt**, the exact replica; the first long random-testing run over every tool; the cache of the original programs' runs |
| 2026-10-24 | **The data panel**: fourteen OpenNeuro subjects chosen to be hard, each with an fMRIPrep run |
| 2026-10-23 and 24 | **3dAutomask and 3dUnifize**, replica and clean-room original each; antsAI's blob alignment |
| 2026-10-23 | **antsRegistration, every stage**: SyN, B-spline, displacement-field, exponential and velocity-field stages |
| 2026-10-22 | **Atropos**, every option |
| 2026-10-21 | **Interactive evidence** on every tool's page |
| 2026-10-20 | **This documentation site** |
| 2026-10-17 and 18 | **antsRegistration's linear stages** and point-set metrics; **antsAI** and **antsAffineInitializer** |
| 2026-10-16 | **ITK transform files**, HDF5 included, read and written in pure Rust |
| 2026-10-11 | **N4BiasFieldCorrection** and **DenoiseImage**; ImageMath's morphology, distance maps and the remaining operations; antsApplyTransforms in single precision; golden tests on six platforms; the first stage-by-stage comparison with fMRIPrep 25.2.6; the originals' defects corrected by default, with a switch that reproduces them |
| 2026-10-10 | **3dTshift**, clean-room original and replica; **the one-shot BOLD resampler**; **the head-motion correction** (clean-room, experimental); ImageMath's arithmetic, ThresholdImage, MultiplyImages and the smoothing and resampling filters |
| By 2026-10-10 | The skeleton with continuous integration on six platforms; **NIfTI-1/2 I/O**, validated against nibabel; **antsApplyTransforms** |
