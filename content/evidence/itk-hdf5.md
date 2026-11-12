---
title: ITK transform files
kicker: Evidence · ANTs and ITK
lede: >-
  ANTs and fMRIPrep keep their transforms in ITK's files: text, MATLAB and HDF5 (`.h5`),
  fMRIPrep's composite `.h5` files among them. LARMORX's port is a replica of ITK 5.4.5's
  reading and writing of these files and of the parts of the HDF5 format they use, in pure Rust,
  with no HDF5 library. Of its record's 149 cases, 128 agree: the replica reads a file's
  datasets as h5py reads them and its transforms as ITK reads them, bit for bit, or writes ITK's
  file byte for byte given ITK's compressed chunks and object times. ITK and the replica refuse
  16 files alike; 5 cases are expected divergences. On fMRIPrep's own composite every dataset reads as the HDF5 library and ITK read
  it, and ITK reads back the file the replica writes.
description: >-
  How LARMORX's replica of ITK's transform files, HDF5 included, compares with ITK 5.4.5, h5py
  and nitransforms: every dataset of a real fMRIPrep .h5 to inspect, the transforms as ITK reads
  them, the file the replica writes, and every case of the record with its verdict.
evidence: true
wide: true
---

<dl class="facts">
<dt>Ports</dt><dd><ul class="ref-ports">
<li class="port port--replica"><span class="port-name">replica</span> <code>larmorx</code> <span class="port-licence">Apache-2.0</span>: translated from ITK 5.4.5's transform reading and writing (Apache-2.0) and from the parts of the HDF5 file format they use, as HDF5 1.12.1 (the version ITK bundles, under The HDF Group's BSD-style licence) reads and lays them out; crates <code>larmorx-hdf5</code> and <code>larmorx-io</code></li>
</ul></dd>
<dt>Status</dt><dd>replica <span class="status-tag status-tag--plain">validated</span> (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/itk-hdf5.md') }}">standard comparison</a> (ITK 5.4.5 on HDF5 1.12.1, h5py, nitransforms) · findings <a href="{{ repo('docs/findings/itk-hdf5.md') }}">itk-hdf5</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/transforms-hdf5.md') }}">transforms-hdf5</a></dd>
</dl>

## What is compared {#what-it-is}

ANTs and fMRIPrep store transforms in ITK's formats: affine matrices as text or MATLAB files, displacement fields as NIfTI vector images, and chains of them as HDF5 composites (fMRIPrep's `*_xfm.h5`). The replica reads and writes them without the HDF5 C library, so they work on every platform the wheels support.

```python
import larmorx as lx

parts = lx.transforms.read("sub-01_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5")
# ITK's class names and parameters:
[(t.name, t.parameters.shape) for t in parts]
lx.transforms.write("copy.h5", parts)
```

On the command line, every ANTs program takes these files, for example `larmorx ants antsApplyTransforms ... -t xfm.h5`. How to read what follows: [how to read the evidence](/validation/#reading).

### Its port {#ports}

ITK comes under the Apache-2.0 licence, as LARMORX does, and HDF5 under a permissive BSD-style one, so the replica is in `larmorx` itself. It is translated from ITK's transform reading and writing and follows HDF5 1.12.1 step by step, so that it reads every dataset as HDF5 does and writes ITK's file byte for byte given ITK's compressed chunks and object times (its own compressed chunks are compared by content). A clean room of ANTs' and ITK's code is planned after FreeSurfer ([roadmap](/roadmap/)).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('itk-hdf5', 'port') }}

The files the replica reads are compared with what h5py reads (every dataset, bit for bit), with what ITK reads (ANTs writes back what it read, in double and in single precision) and with nitransforms' chain. The files it writes are compared with ITK's own files, byte for byte given ITK's compressed chunks and object times, and read back by ITK, h5py and nitransforms. The files ITK refuses are refused alike. The expected divergences are files ITK reads through undefined behaviour or from other files, which the replica refuses, and a composite of 38 transforms laid out differently.

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

## Corrections by default {#corrections}

Where ITK, HDF5 or nitransforms has a deterministic defect that changes a result, the replica corrects it by default, `fix`, and warns. `upstream_defects="reproduce"` (on the command line `--upstream-defects reproduce` from the next release, `LARMORX_UPSTREAM_DEFECTS=reproduce` in 0.1.0rc1) gives their behaviour, and the record compares with it. In reading: a `TransformType` stored as a fixed-length string, as h5py writes it, is read (ITK-12); a parameter dataset of the wrong class or rank is named in the message (ITK-13); parameters wider than 8 bytes (long double, quadruple) are read in the reader's precision, not through float (ITK-14); non-native floats are converted element by element, without the state HDF5 1.12 carries from one to the next (HDF-01); a composite's transforms are read in numeric order, `2` before `10` (PIPE-04), and a file's first group is read when it is not a composite (PIPE-17). In writing: a transform without parameters has its empty parameters stored uncompressed, where ITK fails and leaves a file it cannot read (ITK-15). ITK-16 (a null `TransformType` string, which crashes ITK) and ITK-17 are refused either way. The [API page](repo:docs/api/transforms-hdf5.md) has the table and the [register](repo:docs/findings/upstream-defects.md) every entry. fMRIPrep's composites meet none of them; PIPE-04 would from eleven transforms on.

## Random testing {#random-testing}

Random testing writes random transform files and reads them through ITK, as ANTs' programs do (an ANTs program writes back what it read, in double and in single precision), and through the replica, h5py and nitransforms, in long runs of several hours. The files come from seeded plain arithmetic: text and MATLAB files holding one to four transforms of every linear type ITK reads (in double and float, 2-D and 3-D) and composites, their numbers spelt in many ways, and HDF5 files from the replica's writer, with and without compression, that also hold displacement fields ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest file that still shows it, then fixed and kept as a comparison case, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/itk-hdf5/', 'itk-hdf5') }}

## Known limits {#limits}

The expected divergences: data stored in other files (external raw files, external links, virtual datasets), which ITK's HDF5 follows, are refused; a 2-D component in a 3-D composite is refused (ITK-17, an undefined cast in ITK); a composite of 38 or more transforms is written with its links laid out compactly. Compressed chunks are compared by content, not bytes, by design.

## History {#history}

- **2026-10-16:** compressed chunks compared by content, not bytes, decided (the written files' table and the writing cases say so).
- **2026-10-21:** the standard comparison made (its Generated line).
