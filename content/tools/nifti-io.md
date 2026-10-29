---
title: NIfTI I/O
kicker: Tools · LARMORX
lede: Reading and writing NIfTI-1 and NIfTI-2 images, LARMORX's own implementation in Rust. Every file both libraries read — from 41 OpenNeuro datasets, fMRIPrep's derivatives, templates and two test suites — is read as nibabel reads it, every header field and every value.
description: LARMORX's NIfTI-1/2 reading and writing, validated against nibabel — every header field and the data of real files to inspect, every parity case with its verdict, and speed against nibabel and SimpleITK.
evidence: true
wide: true
---

<dl class="facts">
<dt>Implementation</dt><dd>LARMORX's own (crate <code>larmorx-io</code>), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-larmorx">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/nifti-io.md') }}">nifti-io</a> · benchmark <a href="{{ repo('docs/benchmarks/nifti-io.md') }}">nifti-io</a> · API <a href="{{ repo('docs/api/io.md') }}">io</a></dd>
</dl>

## What it is

Every LARMORX tool reads and writes images through it: NIfTI-1 and NIfTI-2, single files and header/image pairs, compressed or not, every data type nibabel reads but RGB, with scaling, the qform and sform, and compressed writing on several threads.

```python
import larmorx as lx

img = lx.load("sub-01_T1w.nii.gz")          # lx.Image: data, affine, header
lx.save(img, "copy.nii.gz", n_threads=4)
```

How to read what follows: [the validation guide](/validation/#reading).

## The verdicts at a glance {#verdicts}

{{ ev.agreement('nifti-io', 'port') }}

Each file is read by both libraries in every mode nibabel offers (its default array, `get_fdata` in double and single precision, memory-mapped, the stored values), and its header fields, extensions, shape, voxel sizes, scale factors and matrices are compared; then LARMORX writes it and nibabel reads it back. The files both refuse are corrupt or malformed; the expected divergences are RGB data (not supported yet), files whose compression does not match their name (LARMORX reads them by their content), and a single file with `vox_offset` 0 (refused; nibabel reads its header as data).

## Real files, field by field {#example}

Two files of the record: a raw BOLD run as OpenNeuro publishes it, and fMRIPrep's preprocessed output of the same run, which nibabel wrote with a scale factor and an intercept.

{{ ev.table('nifti-io', 'file-0') }}

{{ ev.table('nifti-io', 'file-1') }}

## Every case {#cases}

Each file of the record, with what it is, its verdict and the reason. Search, filter by source or verdict (or select a segment of the chart above), sort by a column; `#case=<path>` links to one.

{{ ev.cases('nifti-io') }}

## Speed {#speed}

{{ ev.speed('nifti-io') }}

## Random testing {#random-testing}

Random testing runs random valid inputs and option combinations through the original program and LARMORX, in long runs of several hours: inputs from seeded plain arithmetic (up to 32³ voxels; orientations, data types, scale factors and value ranges of every kind), with options drawn in random combinations from those the program accepts ([how random testing works](repo:docs/validation/difftest.md)). A difference is shrunk to the smallest input and fewest options that still show it, then fixed and kept as a parity case, registered as a defect of the original, or reported. The latest long run:

{{ ev.random_testing('/tools/nifti-io/') }}

## Known limits {#limits}

RGB data types (RGB24, RGBA32) are not supported yet. The benchmark reads files fully into memory with both libraries; memory mapping is not compared.
