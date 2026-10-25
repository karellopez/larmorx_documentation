---
title: Data panel
kicker: Documentation
lede: The fixed set of shareable datasets every LARMORX tool is validated and shown on, chosen so that no tool's evidence rests on easy data. What each dataset is, why it is there, its licence and citation, and how its faces were checked.
description: The LARMORX data panel — fourteen OpenNeuro subjects at 1.5, 3 and 7 T from Siemens, GE and Philips scanners, with multiband, multi-echo and sparse BOLD, every kind of field map, children, older adults, a tumour and a stroke, head motion and low quality — with each dataset's role, licence, citation and defacing check.
evidence: true
wide: true
---

## Why a fixed panel {#why}

A tool's evidence is only as strong as the data it was shown on. Since 2026-10-24 every tool is to be validated, and its page built, on **one fixed set of datasets**, the same for every tool (the re-validation of the finished tools on it comes next, tool by tool; until then their pages show the data named in each example), chosen for the variety and the difficulty real pipelines meet: field strengths of 1.5, 3 and 7 T; Siemens, GE and Philips scanners; single-band, multiband (4 and 8), multi-echo and sparse BOLD; reversed-phase-encoding, phase-difference, two-phase and direct field maps, linked and unlinked; MPRAGE, MP2RAGE, T2w and FLAIR anatomy; two young children and four older adults; a brain tumour, and a stroke with its manual lesion mask; strong head motion and low quality. Each dataset was chosen after a metadata survey of every public OpenNeuro MRI dataset, and each subject gets an fMRIPrep 25.2.6 run (the table gives each run's state), so a tool's call inside the pipeline can be replayed on it.

On a tool's page, the panel's cases are added beside the existing examples, which all stay as they are: two or three key datasets as whole volumes, the others as three full-resolution slices through the voxel where the tool's output differs most from the original's, the whole field of view shown (3dAutomask's [extreme-motion case](/tools/afni-automask/#panel) is the first); every metric is computed over every voxel of the files.

## The datasets {#datasets}

{{ ev.panel_table() }}

## What each covers {#coverage}

{{ ev.panel_coverage() }}

## Licences, citations and faces {#licences}

Every dataset allows redistribution: ten under a CC0 public-domain dedication, two under the ODC Public Domain Dedication and Licence, one under CC BY 4.0 and one under CC BY-SA. Every example on this site carries the credit line of the data it shows, generated from the same catalog: for CC BY a proper attribution with the changes made, for CC BY-SA also the share-alike notice for the images adapted from it.

**No face is shown.** Every anatomical image of the panel was checked after it was fetched: a mid-sagittal and a para-sagittal slice, and the head's surface seen from the front and from the side at a low threshold (sagittal slices across the face where an MP2RAGE's noisy background hides the surface). Every one is defaced (the face cut away or zeroed, or replaced by MiDeFace's smooth shell) or has no face in its field of view. An image whose face could be recognised would be shown only brain-masked.

{{ ev.panel_details() }}

## Fetch it {#fetch}

The panel lives in LARMORX's test-data catalog ([larmorx-testdata](https://github.com/karellopez/larmorx-testdata), `panel.toml` and `docs/panel.md`), every file pinned to its dataset's snapshot and verified by its SHA-256 and by the snapshot's own content key:

```bash
pip install -e larmorx-testdata
python -m larmorx_testdata fetch --tier full --tag panel
```
