---
title: ITK transform files
kicker: Tools · ANTs and ITK
lede: ITK's transform files — text, MATLAB and HDF5, fMRIPrep's composite .h5 files included — read and written in pure Rust, with no HDF5 library.
description: LARMORX's reading and writing of ITK transform files, HDF5 included, and its validation against ITK 5.4.5, h5py and nitransforms in figures.
---

<dl class="facts">
<dt>Implementation</dt><dd>port of ITK's transform IO and the parts of the HDF5 file format it uses (crates <code>larmorx-hdf5</code>, <code>larmorx-io</code>), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-ants">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/itk-hdf5.md') }}">itk-hdf5</a> · API <a href="{{ repo('docs/api/transforms-hdf5.md') }}">transforms-hdf5</a></dd>
</dl>

## What it is

ANTs and fMRIPrep store transforms in ITK's formats: affine matrices as text or MATLAB files, displacement fields as NIfTI vector images, and chains of them as HDF5 composites (fMRIPrep's `*_xfm.h5`). LARMORX reads and writes them without the HDF5 C library, so they work on every platform the wheels support.

## How to call it

```python
import larmorx as lx

parts = lx.transforms.read("sub-01_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5")
[(t.name, t.parameters.shape) for t in parts]       # ITK's class names and parameters
chain = lx.transforms.load_itk_composite("sub-01_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5")
lx.transforms.write("copy.h5", parts)
```

On the command line, every ANTs program takes these files, e.g. `larmorx ants antsApplyTransforms ... -t xfm.h5`.

## Agreement with ITK, h5py and nitransforms

The [record](repo:docs/validation/itk-hdf5.md) runs 149 cases: 128 pass, 16 files are refused by both and 5 are expected divergences. Read files are compared with what h5py reads (every dataset, bit for bit), with what ITK reads (written back by ANTs, in double and float) and with nitransforms' chain; written files with ITK's own files, byte for byte given ITK's compressed chunks and object times.

{{ figure('itk-hdf5/agreement', "The record's 149 cases by category: read bit for bit (and written files byte for byte), written with the same content, expected divergences and files both refuse.") }}

{{ figure('itk-hdf5/checks', "The record's checks, file by file: datasets and HDF5 storage features as h5py reads them, transforms as ITK reads them in double and float, nitransforms' chain, files ITK refuses, files written (16 of 17 byte-identical to ITK's given its compressed chunks; 12 of 17 with LARMORX's own deflate, the others the same content in other compressed bytes) and the 4 files LARMORX refuses where ITK reads them.") }}

## Speed

No benchmark report yet: reading HDF5 against h5py and ANTs is among the planned benchmarks ([next steps](repo:docs/next-steps.md)).

## Known limits

The expected divergences: data stored in other files (external raw files, external links, virtual datasets), which ITK's HDF5 follows, are refused; a 2-D component in a 3-D composite is refused (ITK-17, an undefined cast in ITK); a composite of 38 or more transforms is written with its links laid out compactly. Compressed chunks are compared by content, not bytes, by design (decided 2026-10-16).
