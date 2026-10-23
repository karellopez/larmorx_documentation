---
title: 3dAutomask
kicker: Tools · AFNI
lede: >-
  AFNI's brain mask of an EPI series or a skull-stripped image, as an exact replica of AFNI's
  source in the separate larmorx-gpl package: bit-identical to AFNI 25.2.09 in every compared
  case, fMRIPrep's own calls included. A clean-room original in LARMORX (Apache-2.0) is still to
  be written from its specification.
description: LARMORX's replica of AFNI's 3dAutomask, validated against AFNI 25.2.09 and fMRIPrep 25.2.6 — fMRIPrep's skull strip of a real BOLD reference, a raw BOLD series and a deliberate correction to inspect, and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementations</dt><dd>exact replica (<code>larmorx-gpl</code>, GPL-3.0-or-later, run as a separate program); clean-room original: not yet, to be written from <a href="{{ repo('specs/3dAutomask.md') }}">specs/3dAutomask.md</a></dd>
<dt>Status</dt><dd><span class="status-tag eco-afni">validated</span> (the replica)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/afni-automask.md') }}">afni-automask</a> · API <a href="{{ repo('docs/api/afni-automask.md') }}">afni-automask</a></dd>
</dl>

## What it is

3dAutomask makes a brain mask from the intensities alone: it averages the absolute values of a series' volumes, finds a clip level from their histogram (gradually, octant by octant, unless `-nograd`), keeps the largest connected cluster above it, peels and unpeels it to cut off thin protrusions, and fills its holes. fMRIPrep calls it once per BOLD run, on its unifized BOLD reference, with `-dilate 1` and `-apply_prefix`: the second skull strip of its BOLD reference workflow.

```bash
larmorx afni 3dAutomask -apply_prefix uni_xform_masked.nii.gz -dilate 1 -prefix uni_xform_mask.nii.gz uni_xform.nii.gz
```

```python
import larmorx as lx

r = lx.afni.automask("uni_xform.nii.gz", dilate=1, apply=True)
r.mask, r.masked
```

3dAutomask's results depend on AFNI library routines copyrighted by the Medical College of Wisconsin (GPL-2), so the replica lives in `larmorx-gpl` (`pip install "larmorx[exact]"`), which LARMORX runs as a separate program; without it `larmorx afni 3dAutomask` stops with a message naming that command. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('afni-automask', 'replica') }}

The replica gives AFNI's bytes, data and NIfTI header, in every case that writes an output, and AFNI's exit status and messages in every case. Where AFNI crashes on a missing option value (AFNI-40), the replica stops with an error instead: the expected divergences. Each case is also run in the default mode, where LARMORX corrects AFNI's deterministic defects and names them.

## In fMRIPrep: the BOLD reference's second skull strip {#example}

fMRIPrep's own call on one of its oracle runs, given to AFNI, to fMRIPrep's build of AFNI and to the replica. Each mask is drawn over the image it was made from; choose *Masked input* above the panels for `-apply_prefix`'s output, and the difference panels for what separates two runs.

{{ ev.example('afni-automask', 'fmriprep-automask') }}

## A raw BOLD series {#bold}

The functional path: with several volumes, 3dAutomask first averages their absolute values, then masks the average.

{{ ev.example('afni-automask', 'bold-automask') }}

## A deliberate correction: AFNI-43 {#correction}

3dAutomask's help says `-peels 0` turns the peeling off; AFNI peels once instead ([AFNI-43](repo:docs/findings/upstream-defects.md)). The replica's default does not peel, and warns; `reproduce` gives AFNI's mask.

{{ ev.example('afni-automask', 'afni-43') }}

## Every case {#cases}

Each case of the record, with what it tests, its command line, the verdict and the reason. Search, filter (or select a segment of the chart above), sort; `#case=<name>` links to one.

{{ ev.cases('afni-automask') }}

## Corrections by default {#corrections}

The replica corrects AFNI's deterministic defects by default and warns: the record's fix pass meets AFNI-43 (`-peels 0`), AFNI-01 (a negative scale factor dropped while averaging a series) and the dataset defects 3dAutomask shares with 3dTshift (AFNI-02, AFNI-07, AFNI-11, AFNI-12, AFNI-16, AFNI-18, AFNI-23, AFNI-26), with `upstream_defects="reproduce"` giving AFNI's behaviour ([register](repo:docs/findings/upstream-defects.md)). AFNI-41, AFNI-42 and AFNI-44 behave as in AFNI until they are decided.

## Known limits {#limits}

LARMORX writes NIfTI only: AFNI's default prefix `automask` is its own dataset format, which the replica refuses (an expected divergence). There is no clean-room original yet, so `implementation="original"` is an error. 3dAutomask is single-threaded in AFNI and in the replica; there is no benchmark report. The other five platforms are held to LARMORX's own Linux output by the [golden tests](repo:docs/validation/golden.md).
