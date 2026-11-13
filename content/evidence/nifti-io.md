---
title: NIfTI I/O
kicker: Evidence · LARMORX
lede: >-
  LARMORX reads and writes NIfTI-1 and NIfTI-2 images with its own code in Rust, compared with
  nibabel 5.4.2 on the files of 41 OpenNeuro datasets, fMRIPrep's derivatives, templates and two
  test suites. In 166 of its 240 compared cases, out of 257, it reads every value, header field
  and matrix as nibabel does, and nibabel reads back what it writes. In the other 69 the data and
  every header field are the same and only the matrices differ, by at most 4.2 × 10⁻¹³ mm, where
  nibabel computes the qform in numpy's 80-bit long double on Linux x86-64 (NIB-04). On one
  thread it reads a gzipped file in up to 6.0 times less time than nibabel.
description: >-
  How LARMORX's own NIfTI-1 and NIfTI-2 reader and writer compares with nibabel 5.4.2: every
  header field and the data of two real files, every case of the record (41 OpenNeuro datasets,
  fMRIPrep's derivatives, templates, two test suites, synthetic files) with its verdict, random
  testing, and speed against nibabel and SimpleITK.
evidence: true
wide: true
---

<dl class="facts">
<dt>Code</dt><dd>LARMORX's own, not a port: crate <code>larmorx-io</code>, <code>lx.load</code>, <code>lx.save</code>, <code>lx.Image</code>, in <code>larmorx</code> (Apache-2.0)</dd>
<dt>Status</dt><dd><span class="status-tag status-tag--plain">validated</span> (<a href="{{ link('/validation/#validated-before') }}">marked before the statuses' definition</a>)</dd>
<dt>Records</dt><dd><a href="{{ repo('docs/validation/nifti-io.md') }}">standard comparison</a> (nibabel 5.4.2) · benchmark <a href="{{ repo('docs/benchmarks/nifti-io.md') }}">nifti-io</a></dd>
<dt>Reference</dt><dd>API page <a href="{{ repo('docs/api/io.md') }}">io</a></dd>
</dl>

## What is compared {#what-it-is}

Every LARMORX program reads and writes images through it: NIfTI-1 and NIfTI-2, single files and header/image pairs, compressed or not, every data type nibabel reads but RGB, with scaling, the qform and sform, and compressed writing on several threads. It is LARMORX's own code, so it is compared with nibabel by its name, never as an original.

```python
import larmorx as lx

img = lx.load("sub-01_T1w.nii.gz")          # lx.Image: data, affine, header
lx.save(img, "copy.nii.gz", n_threads=4)
```

The [API page](repo:docs/api/io.md) describes every function and option. How to read what follows: [how to read the evidence](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('nifti-io', 'port') }}

The [record](repo:docs/validation/nifti-io.md) reads each file with both libraries in every mode nibabel offers: its default array, `get_fdata` in double and single precision, memory-mapped, and the stored values. It compares their header fields, extensions, shape, voxel sizes, scale factors and matrices. Then LARMORX writes the file and nibabel reads it back.

- The 17 files both refuse are corrupt or malformed.
- The 5 expected divergences are RGB data (not supported yet), files whose compression does not match their name (LARMORX reads them by their content), and a single file with `vox_offset` 0 (refused; nibabel reads its header as data).
- In the 69 files whose matrices differ, nibabel's own matrices change with the platform: computed in double, as nibabel computes them where long double is 64 bits (arm64, Windows), they are LARMORX's bit for bit ([NIB-04](repo:docs/findings/upstream-defects.md)).

## Real files, field by field {#example}

Two files of the record: a raw BOLD run as OpenNeuro publishes it, and fMRIPrep's preprocessed output of the same run, which nibabel wrote with a scale factor and an intercept.

{{ ev.table('nifti-io', 'file-0') }}

{{ ev.table('nifti-io', 'file-1') }}

## Every case {#cases}

Each file of the record, with what it is, its verdict and the reason. Search, filter by source or verdict (or select a segment of the chart above), sort by a column; `#case=<path>` links to one.

{{ ev.cases('nifti-io') }}

## Speed {#speed}

The benchmark ([report](repo:docs/benchmarks/nifti-io.md)) reads and writes each file with both libraries and SimpleITK, the files in the system's page cache, so it times parsing, decompression and conversion, not the disk. Writing compressed files on several threads is in the report.

{{ ev.speed('nifti-io') }}

## Random testing {#random-testing}

Random testing runs random valid inputs through nibabel and LARMORX's own reader and writer, in long runs of several hours. The inputs come from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), the options in random combinations ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a permanent case, registered as a defect of nibabel, or reported. The latest long run:

{{ ev.random_testing('/tools/nifti-io/', 'nifti-io') }}

## Known limits {#limits}

RGB data types (RGB24, RGBA32) are not supported yet. The benchmark reads files fully into memory with both libraries; memory mapping is not compared.

## History {#history}

- **2026-11-08**: `lx.io.load_nibabel` gives nibabel's matrices of x86-64 Linux, its extended precision emulated exactly on every platform; `lx.load` keeps double precision everywhere (NIB-04, [the register](repo:docs/findings/upstream-defects.md)).
