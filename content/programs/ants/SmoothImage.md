---
title: "`SmoothImage`"
kicker: "Programs · ANTs and ITK"
description: "LARMORX reference for ANTs 2.6.5 `SmoothImage`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants SmoothImage"
  python: "lx.ants.smooth_image"
  api: "docs/api/ants-smooth-image.md"
  evidence: "/evidence/ants-programs/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/smooth_image.rs: "e6df9d79a4c32be2"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "24c23485c8957683"
    docs/api/ants-smooth-image.md: "8858339c095547ad"
    python/larmorx/ants/smoothing.py: "be224e100de8754e"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

`SmoothImage` smooths an image with a Gaussian of a given sigma, in voxels or in millimetres, or
filters it with a median over a box of a given radius.

## Command line {#command-line}

```text synopsis
larmorx ants SmoothImage ImageDimension image.ext smoothingsigma outimage.ext {sigma-is-in-spacing-units-(0)/1} {medianfilter-(0)/1}
```

Everything after `larmorx ants SmoothImage` is the original's command line: the arguments of ANTs 2.6.5's `SmoothImage`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants SmoothImage ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>SmoothImage</code>'s usage text, as the replica prints it</summary>

```text
Usage:
SmoothImage ImageDimension image.ext smoothingsigma outimage.ext {sigma-is-in-spacing-units-(0)/1} {medianfilter-(0)/1}
 If using median filter, sigma is the radius of filtering, in voxels
 A separate sigma can be specified for each dimension, e.g., 1.5x1x2
```

</details>

## Python {#python}

```python
lx.ants.smooth_image(
    image: Any,
    sigma: float | Sequence[float],
    *,
    sigma_in_physical_units: bool = False,
    median: bool = False,
    n_threads: int = 1,
) -> Image
```

`SmoothImage d in sigma out [physical] [median]`: Gaussian smoothing with ITK's `SmoothingRecursiveGaussianImageFilter`.

Returns a float32 `lx.Image` on the input's grid; `sigma` is a number or one per axis.

```python
import larmorx as lx

smoothed = lx.ants.smooth_image("sub-01_T1w.nii.gz", 1.5)                 # sigma 1.5 voxels
smoothed = lx.ants.smooth_image(t1w, [2.0, 2.0, 3.0], sigma_in_physical_units=True)
filtered = lx.ants.smooth_image(t1w, 1, median=True)                      # 3x3x3 median
```

Its result, `Image`, holds a voxel array placed in world space by an affine.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">data</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">affine</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">header</span></code> | <code><span class="nw">NiftiHeader</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">Implementation</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `SmoothImage` accepts (`crates/larmorx-ants/src/cli/smooth_image.rs`) and the arguments of `lx.ants.smooth_image` (`python/larmorx/ants/smoothing.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs argument (positional) | Python | Default | Notes |
|---|---|---|---|
| 1 <code><span class="nw">ImageDimension</span></code> (2, 3, 4) | – |  | the image's own dimensions; a 4D image is smoothed along time too (the time step is its spacing) |
| 2 <code><span class="nw">image&#46;ext</span></code> | <code><span class="nw">image</span></code> |  | path, <code><span class="nw">lx&#46;Image</span></code>, nibabel image or <code><span class="nw">&#40;array&#44;</span> <span class="nw">affine&#41;</span></code>; read as <code><span class="nw">float</span></code> |
| 3 <code><span class="nw">smoothingsigma</span></code> (<code><span class="nw">1&#46;5</span></code> or <code><span class="nw">1x1x2</span></code>) | <code><span class="nw">sigma</span></code> |  | a number or one per axis; in voxels: multiplied by the spacing **in float**, as ANTs does |
| 4 <code><span class="nw">outimage&#46;ext</span></code> | the result |  | float32, the input's grid |
| 5 <code><span class="nw">sigma&#45;is&#45;in&#45;spacing&#45;units</span></code> (<code><span class="nw">1</span></code>) | <code><span class="nw">sigma&#95;in&#95;physical&#95;units&#61;True</span></code> | <code><span class="nw">False</span></code> | sigma in mm (s for time) |
| 6 <code><span class="nw">medianfilter</span></code> (<code><span class="nw">1</span></code>) | <code><span class="nw">median&#61;True</span></code> | <code><span class="nw">False</span></code> | <code><span class="nw">MedianImageFilter</span></code>, radius <code><span class="nw">int&#40;sigma&#41;</span></code> voxels per axis |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code> (or <code><span class="nw">NSLOTS</span></code>, as ITK reads them) | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants SmoothImage ...`); `lx.ants.smooth_image` takes `n_threads` as an argument, and the others are the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;smooth&#95;image</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;smooth&#95;image</span></code> takes no <code><span class="nw">upstream&#95;defects</span></code>. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `t1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# A Gaussian of sigma 1.5 voxels, and a median over 3 x 3 x 3 voxels.
smoothed = lx.ants.smooth_image("t1w.nii.gz", 1.5)
smoothed.shape  # -> (40, 48, 40)
filtered = lx.ants.smooth_image("t1w.nii.gz", 1, median=True)
filtered.data.dtype  # -> dtype('float32')
```

```bash
larmorx ants SmoothImage 3 t1w.nii.gz 1.5 smoothed.nii.gz
larmorx ants SmoothImage 3 t1w.nii.gz 2x2x3 smoothed_mm.nii.gz 1
larmorx ants SmoothImage 3 t1w.nii.gz 1 median.nii.gz 0 1
```

## Ports {#ports}

`SmoothImage` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-smooth-image](repo:docs/validation/ants-smooth-image.md) |

**The replica: status `validated`** against SmoothImage itself (its
[record](repo:docs/validation/ants-smooth-image.md), 2026-10-12): 38 cases, 30 outputs compared, all
bit-identical with ANTs' exact header bytes, in 2, 3 and 4 dimensions; 7 rejected by both alike.
Compared with ANTs' defects reproduced (`LARMORX_UPSTREAM_DEFECTS=reproduce`); the record's "D13
fix pass" lists what larmorx's default changes.

**On the data panel** ([record](repo:docs/validation/ants-smooth-image-panel.md), 2026-10-26): fMRIPrep
25.2.6 never calls `SmoothImage`; on the panel's images (a 2 mm Gaussian of the 7 T MP2RAGE, 1.5
mm of the 82-year-old's FLAIR, a median of a child's T1w, a 4D Gaussian of a 588-volume multiband
series): **4 of 4 bit-identical, header bytes included**; a zero sigma along time is refused by
both.

`SmoothImage` has one port, in `pip install larmorx`: **the replica** (`crates/larmorx-ants`,
`crates/larmorx-image`; Apache-2.0; Rust `larmorx_ants::smooth_image`, `larmorx_image::gaussian`,
`larmorx_image::median`), translated from ANTs 2.6.5 on ITK 5.4.5 (Apache-2.0).

## Evidence {#evidence}

How each of `SmoothImage`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-programs/).

## More in the repository {#more}

The API page [docs/api/ants-smooth-image.md](repo:docs/api/ants-smooth-image.md) holds what `SmoothImage` shares with the page's other programs:

- [Speed](repo:docs/api/ants-smooth-image.md#speed)
- [Behaviour worth knowing](repo:docs/api/ants-smooth-image.md#behaviour-worth-knowing)
- [Upstream defects (D13)](repo:docs/api/ants-smooth-image.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/ants-smooth-image.md#deliberate-differences)
