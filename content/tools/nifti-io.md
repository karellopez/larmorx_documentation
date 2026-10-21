---
title: NIfTI I/O
kicker: Tools · LARMORX
lede: Reading and writing NIfTI-1 and NIfTI-2 images, LARMORX's own implementation in Rust. Every file both read is read as nibabel reads it.
description: LARMORX's NIfTI-1/2 reading and writing, its validation against nibabel in figures, and its speed against nibabel and SimpleITK.
---

<dl class="facts">
<dt>Implementation</dt><dd>LARMORX's own (crate <code>larmorx-io</code>), in <code>larmorx</code></dd>
<dt>Status</dt><dd><span class="status-tag eco-larmorx">validated</span></dd>
<dt>Record</dt><dd><a href="{{ repo('docs/validation/nifti-io.md') }}">nifti-io</a> · benchmark <a href="{{ repo('docs/benchmarks/nifti-io.md') }}">nifti-io</a> · API <a href="{{ repo('docs/api/io.md') }}">io</a></dd>
</dl>

## What it is

Every LARMORX tool reads and writes images through it: NIfTI-1 and NIfTI-2, single files and header/image pairs, compressed or not, every data type nibabel reads but RGB, with scaling, the qform and sform, and compressed writing on several threads.

## How to call it

```python
import larmorx as lx

img = lx.load("sub-01_T1w.nii.gz")          # lx.Image: data, affine, header
lx.save(img, "copy.nii.gz", n_threads=4)
```

## Agreement with nibabel

The [record](repo:docs/validation/nifti-io.md) reads 252 files: real datasets from 43 OpenNeuro collections, fMRIPrep derivatives, templates, ITK's and nibabel's test files, and synthetic files for every data type, layout, orientation, scaling and malformation. 230 are read as nibabel reads them (data, header and affine), 17 are refused by both and 5 are expected divergences: RGB24 and RGBA32 data are not supported yet; a file compressed or not regardless of its name is read by its content, where nibabel fails; a single file with `vox_offset` 0 is refused, where nibabel reads its header as data.

{{ figure('nifti-io/agreement', "The record's 252 files, by source: read as nibabel reads them, refused by both, and the expected divergences.") }}

## Speed

{{ figure('nifti-io/speed-read', "Median seconds to read each compressed file of the benchmark report into memory with nibabel, SimpleITK and LARMORX at 1 and 12 threads (files in the page cache), from the report of 2026-10-09 (Intel i7-8750H, 12 logical CPUs); the factor is LARMORX's speed-up over nibabel at one thread.") }}

{{ figure('nifti-io/speed-write', "The same files written compressed, each tool at its default compression level (nibabel 1, LARMORX 2, SimpleITK 6; the report also compares LARMORX and nibabel at level 6).") }}

## Known limits

RGB data types (RGB24, RGBA32) are not supported yet. The benchmark report reads uncompressed files fully into memory with both libraries; memory mapping is not compared.
