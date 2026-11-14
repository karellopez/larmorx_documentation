---
title: "`MultiplyImages`"
kicker: "Programs · ANTs and ITK"
lede: "`MultiplyImages` multiplies an image by another image or by a number."
description: "LARMORX reference for ANTs 2.6.5 `MultiplyImages`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants MultiplyImages"
  python: "lx.ants.multiply_images"
  api: "docs/api/ants-multiply-images.md"
  evidence: "/evidence/ants-programs/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/multiply_images.rs: "69f7fdad2ceade62"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "bf883da07a0caa93"
    docs/api/ants-multiply-images.md: "9ecb7b61e631166b"
    python/larmorx/ants/threshold.py: "8eb31db682525d28"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

sMRIPrep's brain
extraction runs it three times after Atropos (`08_mult_gm`, `09_relabel_wm` and
`12_relabel_gm`).

## Command line {#command-line}

```text synopsis
larmorx ants MultiplyImages ImageDimension img1.nii img2.nii product.nii
larmorx ants MultiplyImages ImageDimension img1.nii 2.5 product.nii
```

Everything after `larmorx ants MultiplyImages` is the original's command line: the arguments of ANTs 2.6.5's `MultiplyImages`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants MultiplyImages ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>MultiplyImages</code>'s usage text, as the replica prints it</summary>

```text
Usage:
MultiplyImages ImageDimension img1.nii img2.nii product.nii {smoothing}
 2nd image file may also be floating point numerical value, and program will act accordingly -- i.e. read as a number.
 Program handles vector and tensor images as well (larmorx: scalar images only)
```

</details>

## Python {#python}

```python
lx.ants.multiply_images(
    image: Any,
    other: Any,
    *,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
) -> Image
```

Where `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

`MultiplyImages d image other out`: the voxel-wise product in float32, with `other` a number or an image (read at `image`'s voxel indices; its geometry is ignored, as in ANTs).

Returns the float32 product at `image`'s voxel indices, as an `lx.Image`; `other` is an image or
a number. A path that does not exist raises `FileNotFoundError`.

```python
import larmorx as lx

brain = lx.ants.multiply_images("t1w.nii.gz", "brain_mask.nii.gz")
half = lx.ants.multiply_images(gm_probseg, 0.5)
```

Its result, `Image`, holds a voxel array placed in world space by an affine.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">data</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">affine</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">header</span></code> | <code><span class="nw">NiftiHeader</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">Implementation</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `MultiplyImages` accepts (`crates/larmorx-ants/src/cli/multiply_images.rs`) and the arguments of `lx.ants.multiply_images` (`python/larmorx/ants/threshold.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs argument (positional) | Python | Default | Notes |
|---|---|---|---|
| 1 <code><span class="nw">ImageDimension</span></code> | – |  | 2, 3, 4 (ANTs also accepts 1); Python takes any array shape |
| 2 <code><span class="nw">img1</span></code> | <code><span class="nw">image</span></code> |  | the product is at its voxel indices |
| 3 <code><span class="nw">img2</span></code> or a number | <code><span class="nw">other</span></code> |  | an image (its geometry is ignored: it may be larger; smaller is ANTS-07 in [Upstream defects](repo:docs/api/ants-multiply-images.md#upstream-defects-d13)) or a number; vector and tensor images are not supported yet (ANTs multiplies component by component) |
| 4 <code><span class="nw">product</span></code> | the result |  | without an output name ANTs prints "missing output filename" and aborts; larmorx exits 1 |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code> | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">fix</span></code> (default) or <code><span class="nw">reproduce</span></code> ([Upstream defects](repo:docs/api/ants-multiply-images.md#upstream-defects-d13)) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants MultiplyImages ...`); `lx.ants.multiply_images` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;multiply&#95;images</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `t1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `mask.nii.gz` (the synthetic head's brain as a mask (1 inside, 0 outside)). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# The brain of the head: the image times its mask.
brain = lx.ants.multiply_images("t1w.nii.gz", "mask.nii.gz")
brain.data.dtype  # -> dtype('float32')
```

```bash
larmorx ants MultiplyImages 3 t1w.nii.gz mask.nii.gz brain.nii.gz
larmorx ants MultiplyImages 3 t1w.nii.gz 0.5 half.nii.gz
```

## Ports {#ports}

`MultiplyImages` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-multiply-images](repo:docs/validation/ants-multiply-images.md) |

**The replica: status `validated`** against MultiplyImages itself (its
[record](repo:docs/validation/ants-multiply-images.md), 2026-10-12): 15 cases, 12 compared, 3 rejected
by both alike; every compared case bit-identical, with ANTs' exact header bytes. Compared with
ANTs' defects reproduced (`LARMORX_UPSTREAM_DEFECTS=reproduce`); the record's "D13 fix pass" lists
what larmorx's default changes.

**On the data panel** ([record](repo:docs/validation/ants-multiply-images-panel.md), 2026-10-26): all
42 `MultiplyImages` nodes of the fourteen finished oracle runs (the three of sMRIPrep's brain
extraction after Atropos, `08_mult_gm`, `09_relabel_wm` and `12_relabel_gm`, in every run), each
replayed from its node with its inputs, and two calls fMRIPrep never makes (the stroke's T2w times
its lesion mask, a 588-volume multiband series times a scalar): **44 of 44 bit-identical, header
bytes included**.

`MultiplyImages` has one port, in `pip install larmorx`: **the replica** (`crates/larmorx-ants`;
Apache-2.0; Rust `larmorx_ants::multiply_images`), translated from ANTs 2.6.5 (Apache-2.0).

## Evidence {#evidence}

How each of `MultiplyImages`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-programs/).

## More in the repository {#more}

The API page [docs/api/ants-multiply-images.md](repo:docs/api/ants-multiply-images.md) holds what `MultiplyImages` shares with the page's other programs:

- [Speed](repo:docs/api/ants-multiply-images.md#speed)
- [Behaviour worth knowing](repo:docs/api/ants-multiply-images.md#behaviour-worth-knowing)
- [Upstream defects (D13)](repo:docs/api/ants-multiply-images.md#upstream-defects-d13)
