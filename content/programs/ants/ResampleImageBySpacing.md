---
title: "`ResampleImageBySpacing`"
kicker: "Programs · ANTs and ITK"
description: "LARMORX reference for ANTs 2.6.5 `ResampleImageBySpacing`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants ResampleImageBySpacing"
  python: "lx.ants.resample_image_by_spacing"
  api: "docs/api/ants-resample-image-by-spacing.md"
  evidence: "/evidence/ants-programs/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/resample_image_by_spacing.rs: "a485235a406e8659"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "91be42d24bb3ba2b"
    docs/api/ants-resample-image-by-spacing.md: "66559e74e1ed8058"
    python/larmorx/ants/resample.py: "52c82202b43379af"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

`ResampleImageBySpacing` resamples an image onto a grid with a new spacing, keeping its origin
and direction, after smoothing it with a Gaussian where the spacing grows, by linear or
nearest-neighbour interpolation.

## Command line {#command-line}

```text synopsis
larmorx ants ResampleImageBySpacing ImageDimension inputImageFile outputImageFile outxspc outyspc {outzspacing} {dosmooth?} {addvox} {nn-interp?}
```

Everything after `larmorx ants ResampleImageBySpacing` is the original's command line: the arguments of ANTs 2.6.5's `ResampleImageBySpacing`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants ResampleImageBySpacing ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>ResampleImageBySpacing</code>'s usage text, as the replica prints it</summary>

```text
Usage:
ResampleImageBySpacing  ImageDimension inputImageFile  outputImageFile outxspc outyspc {outzspacing}  {dosmooth?}  {addvox} {nn-interp?}
 addvox pads each dimension by addvox
```

</details>

## Python {#python}

```python
lx.ants.resample_image_by_spacing(
    image: Any,
    spacing: Sequence[float],
    *,
    smooth: bool = True,
    add_voxels: int = 0,
    nearest: bool = False,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
) -> Image
```

Where `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

`ResampleImageBySpacing d in out sx sy [sz [st]] smooth addvox nn`: the image resampled onto a grid with the same origin and direction and the new `spacing` (one value per axis; for a 4D image the last is the time step in seconds).

Returns a float32 `lx.Image` with the new spacing; the Python result keeps the input's header,
with the new time step in 4D.

```python
import larmorx as lx

low = lx.ants.resample_image_by_spacing("sub-01_T1w.nii.gz", [2.0, 2.0, 2.0])
up = lx.ants.resample_image_by_spacing(boldref, [1.0, 1.0, 1.0], smooth=False)
labels = lx.ants.resample_image_by_spacing(seg, [1, 1, 1], smooth=False, nearest=True)
```

Its result, `Image`, holds a voxel array placed in world space by an affine.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">data</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">affine</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">header</span></code> | <code><span class="nw">NiftiHeader</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">Implementation</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `ResampleImageBySpacing` accepts (`crates/larmorx-ants/src/cli/resample_image_by_spacing.rs`) and the arguments of `lx.ants.resample_image_by_spacing` (`python/larmorx/ants/resample.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs argument (positional) | Python | Default | Notes |
|---|---|---|---|
| 1 <code><span class="nw">ImageDimension</span></code> (2, 3, 4) | <code><span class="nw">len&#40;spacing&#41;</span></code> |  | a path is read in that many dimensions; an in-memory image must have them |
| 2 <code><span class="nw">inputImageFile</span></code> | <code><span class="nw">image</span></code> |  | path, <code><span class="nw">lx&#46;Image</span></code>, nibabel image or <code><span class="nw">&#40;array&#44;</span> <span class="nw">affine&#41;</span></code>; read as <code><span class="nw">float</span></code> |
| 3 <code><span class="nw">outputImageFile</span></code> | the result |  | float32; same origin and direction, the new spacing |
| 4 <code><span class="nw">outxspc</span></code>, 5 <code><span class="nw">outyspc</span></code>, then <code><span class="nw">outzspacing</span></code> (and the time step in 4D) | <code><span class="nw">spacing</span></code> |  | one value per axis (<code><span class="nw">atof</span></code>); 4D: the last is the time step in seconds |
| <code><span class="nw">dosmooth&#63;</span></code> (default 1), after the spacings | <code><span class="nw">smooth&#61;True</span></code> | <code><span class="nw">True</span></code> | per axis, a recursive Gaussian of sigma <code><span class="nw">out&#47;in</span> <span class="nw">&#8722;</span> <span class="nw">1</span></code> input voxels where positive (ANTs: the same number in mm, ANTS-32) |
| <code><span class="nw">addvox</span></code> (default 0), after it | <code><span class="nw">add&#95;voxels&#61;0</span></code> | <code><span class="nw">0</span></code> | added to every axis's size |
| <code><span class="nw">nn&#45;interp&#63;</span></code> (default 0), last | <code><span class="nw">nearest&#61;False</span></code> | <code><span class="nw">False</span></code> | nearest neighbour instead of linear |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code> (or <code><span class="nw">NSLOTS</span></code>, as ITK reads them) | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants ResampleImageBySpacing ...`); `lx.ants.resample_image_by_spacing` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;resample&#95;image&#95;by&#95;spacing</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `t1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `mask.nii.gz` (the synthetic head's brain as a mask (1 inside, 0 outside)). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# The 4 mm head to 8 mm, smoothed first; the mask to 2 mm by nearest neighbour.
low = lx.ants.resample_image_by_spacing("t1w.nii.gz", [8.0, 8.0, 8.0])
low.shape  # -> (20, 24, 20)
labels = lx.ants.resample_image_by_spacing("mask.nii.gz", [2, 2, 2], smooth=False, nearest=True)
labels.shape  # -> (80, 96, 80)
```

```bash
larmorx ants ResampleImageBySpacing 3 t1w.nii.gz t1w_8mm.nii.gz 8 8 8
larmorx ants ResampleImageBySpacing 3 mask.nii.gz mask_2mm.nii.gz 2 2 2 0 0 1
```

## Ports {#ports}

`ResampleImageBySpacing` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-resample-image-by-spacing](repo:docs/validation/ants-resample-image-by-spacing.md) |

**The replica: status `validated`** against ResampleImageBySpacing itself (its
[record](repo:docs/validation/ants-resample-image-by-spacing.md), 2026-10-24): 37 cases, 30 outputs
compared, all bit-identical with ANTs' exact header bytes and printed text, in 2, 3 and 4
dimensions; 5 rejected by both alike. Where ANTs resamples uninitialised memory, larmorx
reproduces the rest (exit code, header, printed text) and fills that memory with zeros
(ANTS-28). Compared with ANTs' defects reproduced (`LARMORX_UPSTREAM_DEFECTS=reproduce`); the
record's "D13 fix pass" lists what larmorx's default changes.

**On the data panel** ([record](repo:docs/validation/ants-resample-image-by-spacing-panel.md),
2026-10-26): fMRIPrep 25.2.6 never calls `ResampleImageBySpacing`; on the panel's images (the 7 T
MP2RAGE to 2 mm, the 82-year-old's FLAIR to 1 mm, the 3.5-year-old's T1w to 1.5 mm): **3 of 3
bit-identical, header bytes included**.

`ResampleImageBySpacing` has one port, in `pip install larmorx`: **the replica**
(`crates/larmorx-ants`, `crates/larmorx-image`; Apache-2.0; Rust
`larmorx_ants::resample_image_by_spacing`, `larmorx_ants::resample`), translated from ANTs 2.6.5
on ITK 5.4.5 (Apache-2.0).

## Evidence {#evidence}

How each of `ResampleImageBySpacing`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-programs/).

## More in the repository {#more}

The API page [docs/api/ants-resample-image-by-spacing.md](repo:docs/api/ants-resample-image-by-spacing.md) holds what `ResampleImageBySpacing` shares with the page's other programs:

- [Speed](repo:docs/api/ants-resample-image-by-spacing.md#speed)
- [Behaviour worth knowing](repo:docs/api/ants-resample-image-by-spacing.md#behaviour-worth-knowing)
- [Upstream defects (D13)](repo:docs/api/ants-resample-image-by-spacing.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/ants-resample-image-by-spacing.md#deliberate-differences)
