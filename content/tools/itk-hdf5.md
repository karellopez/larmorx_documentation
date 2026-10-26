---
title: ITK transform files
kicker: Tools · ANTs and ITK
lede: ITK's transform files — text, MATLAB and HDF5, fMRIPrep's composite .h5 files included — read and written in pure Rust, with no HDF5 library. Every dataset of fMRIPrep's own composite reads as the HDF5 library and ITK read it, and ITK reads back what LARMORX writes.
description: LARMORX's reading and writing of ITK transform files, HDF5 included, validated against ITK 5.4.5, h5py and nitransforms — every dataset of a real fMRIPrep .h5 to inspect, the transforms as ITK reads them, the files LARMORX writes, and every parity case with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ITK's transform IO and the parts of the HDF5 file format it uses (crates <code>larmorx-hdf5</code>, <code>larmorx-io</code>), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/itk-hdf5.md') }}">itk-hdf5</a> · API <a href="{{ repo('docs/api/transforms-hdf5.md') }}">transforms-hdf5</a></dd>
</dl>

## What it is

ANTs and fMRIPrep store transforms in ITK's formats: affine matrices as text or MATLAB files, displacement fields as NIfTI vector images, and chains of them as HDF5 composites (fMRIPrep's `*_xfm.h5`). LARMORX reads and writes them without the HDF5 C library, so they work on every platform the wheels support.

```python
import larmorx as lx

parts = lx.transforms.read("sub-01_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5")
[(t.name, t.parameters.shape) for t in parts]       # ITK's class names and parameters
lx.transforms.write("copy.h5", parts)
```

On the command line, every ANTs program takes these files, e.g. `larmorx ants antsApplyTransforms ... -t xfm.h5`. How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('itk-hdf5', 'port') }}

Read files are compared with what h5py reads (every dataset, bit for bit), with what ITK reads (ANTs writes back what it read, in double and in single precision) and with nitransforms' chain; written files with ITK's own files, byte for byte given ITK's compressed chunks and object times, and read back by ITK, h5py and nitransforms. The files ITK refuses are refused alike; the expected divergences are files ITK reads through undefined behaviour or from other files, which LARMORX refuses, and a composite of 38 transforms laid out differently.

## A real file, object by object {#example}

fMRIPrep 25.2.6's T1w-to-MNI152NLin2009cAsym composite of OpenNeuro ds000005 sub-01 (PDDL-1.0): the affine of its template registration and the SyN displacement field, 25.6 million values on the 1 mm template grid. Each table is one of the comparisons the record makes for every file.

{{ ev.table('itk-hdf5', 'objects') }}

{{ ev.table('itk-hdf5', 'transforms') }}

{{ ev.table('itk-hdf5', 'written') }}

## Every case {#cases}

Each case of the record, with what it tests, its verdict and the reason. Search, filter by category or verdict (or select a segment of the chart above), sort by a column; `#case=<name>` links to one.

{{ ev.cases('itk-hdf5') }}

## Speed {#speed}

No benchmark report yet: reading HDF5 against h5py and ANTs is among the planned benchmarks ([next steps](repo:docs/next-steps.md)).

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, a night at a time: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest night:

{{ ev.random_testing('/tools/itk-hdf5/') }}

## Known limits {#limits}

The expected divergences: data stored in other files (external raw files, external links, virtual datasets), which ITK's HDF5 follows, are refused; a 2-D component in a 3-D composite is refused (ITK-17, an undefined cast in ITK); a composite of 38 or more transforms is written with its links laid out compactly. Compressed chunks are compared by content, not bytes, by design (decided 2026-10-16).
