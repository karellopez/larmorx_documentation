---
title: "`ResampleImage`"
kicker: "Programs · ANTs and ITK"
description: "LARMORX reference for ANTs 2.6.5 `ResampleImage`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants ResampleImage"
  python: "lx.ants.resample_image"
  api: "docs/api/ants-resample-image.md"
  evidence: "/evidence/ants-programs/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/resample_image.rs: "1a9452439d9e28fb"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "be80bfe4fac23290"
    docs/api/ants-resample-image.md: "61093fb0766557ea"
    python/larmorx/ants/resample.py: "52c82202b43379af"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

`ResampleImage` resamples an image onto a grid with a new spacing or a new size, keeping its
origin and direction, by linear, nearest-neighbour, Gaussian, windowed-sinc or B-spline
interpolation, and writes it in one of ANTs' eight pixel types.

## Command line {#command-line}

```text synopsis
larmorx ants ResampleImage imageDimension inputImage outputImage MxNxO [size=1,spacing=0] [interpolate type] [pixeltype]
```

Everything after `larmorx ants ResampleImage` is the original's command line: the arguments of ANTs 2.6.5's `ResampleImage`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants ResampleImage ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>ResampleImage</code>'s usage text, as the replica prints it</summary>

```text
Usage: ResampleImage imageDimension inputImage outputImage MxNxO [size=1,spacing=0] [interpolate type [its parameters]] [pixeltype]
  Interpolation type:
    0. linear (default)
    1. nn
    2. gaussian [sigma=imageSpacing] [alpha=1.0]
    3. windowedSinc [type = 'c'osine, 'w'elch, 'b'lackman, 'l'anczos, 'h'amming]
    4. B-Spline [order=3]
 pixeltype  :  TYPE
  0  :  char
  1  :  unsigned char
  2  :  short
  3  :  unsigned short
  4  :  int
  5  :  unsigned int
  6  :  float (default)
  7  :  double
 larmorx reads an interpolation type's parameters right after it, and the pixel type after
 them (LARMORX_UPSTREAM_DEFECTS=reproduce reads the seventh argument as both, as ANTs does).
```

</details>

## Python {#python}

```python
lx.ants.resample_image(
    image: Any,
    spacing: float | Sequence[float] | None = None,
    *,
    size: int | Sequence[int] | None = None,
    interpolation: str = "linear",
    sigma: float | Sequence[float] | None = None,
    alpha: float = 1.0,
    window: str = "hamming",
    order: int = 3,
    pixel_type: str = "float",
    dimension: int | None = None,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
) -> Image
```

Where `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

`ResampleImage d in out MxNxO [size?] [interpolation] [pixeltype]`: the image resampled onto a grid with the same origin and direction and a new `spacing` or `size` (one value or one per axis), without smoothing.

Returns an `lx.Image` in `pixel_type`'s type. Give `spacing` or `size`, one value or one per
axis.

```python
import larmorx as lx

t1w_2mm = lx.ants.resample_image("sub-01_T1w.nii.gz", 2.0)
on_grid = lx.ants.resample_image(t1w, size=[128, 128, 96], interpolation="bspline")
labels = lx.ants.resample_image(seg, 1.0, interpolation="nearest", pixel_type="short")
```

Its result, `Image`, holds a voxel array placed in world space by an affine.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">data</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">affine</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">header</span></code> | <code><span class="nw">NiftiHeader</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">Implementation</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `ResampleImage` accepts (`crates/larmorx-ants/src/cli/resample_image.rs`) and the arguments of `lx.ants.resample_image` (`python/larmorx/ants/resample.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs argument (positional) | Python | Default | Notes |
|---|---|---|---|
| 1 <code><span class="nw">imageDimension</span></code> (2, 3, 4) | <code><span class="nw">dimension</span></code> (default: the image's) | <code><span class="nw">None</span></code> | a path is read in that many dimensions |
| 2 <code><span class="nw">inputImage</span></code>, 3 <code><span class="nw">outputImage</span></code> | <code><span class="nw">image</span></code>, the result |  | the output keeps the input's origin and direction |
| 4 <code><span class="nw">MxNxO</span></code>, 5 <code><span class="nw">0</span></code> (default) | <code><span class="nw">spacing</span></code> (one value or one per axis) | <code><span class="nw">None</span></code> | size <code><span class="nw">int&#40;old</span> <span class="nw">spacing</span> <span class="nw">&#183;</span> <span class="nw">old</span> <span class="nw">size</span> <span class="nw">&#47;</span> <span class="nw">spacing</span> <span class="nw">&#43;</span> <span class="nw">0&#46;5&#41;</span></code> |
| 4 <code><span class="nw">MxNxO</span></code>, 5 <code><span class="nw">1</span></code> | <code><span class="nw">size&#61;</span></code> (one value or one per axis) | <code><span class="nw">None</span></code> | spacing <code><span class="nw">old</span> <span class="nw">&#183;</span> <span class="nw">&#40;old</span> <span class="nw">size</span> <span class="nw">&#8722;</span> <span class="nw">1&#41;</span> <span class="nw">&#47;</span> <span class="nw">&#40;size</span> <span class="nw">&#8722;</span> <span class="nw">1&#41;</span></code> |
| 6 interpolation <code><span class="nw">0</span></code> (default) / <code><span class="nw">1</span></code> | <code><span class="nw">interpolation&#61;&#34;linear&#34;</span></code> / <code><span class="nw">&#34;nearest&#34;</span></code> | <code><span class="nw">&#34;linear&#34;</span></code> | any dimension |
| 6 <code><span class="nw">2</span></code>, then <code><span class="nw">sigma</span></code> and <code><span class="nw">alpha</span></code> | <code><span class="nw">&#34;gaussian&#34;</span></code>, <code><span class="nw">sigma&#61;</span></code>, <code><span class="nw">alpha&#61;1&#46;0</span></code> | <code><span class="nw">sigma&#61;None</span></code>, <code><span class="nw">alpha&#61;1&#46;0</span></code> | sigma in mm, default the input spacing; 3D |
| 6 <code><span class="nw">3</span></code>, then the window | <code><span class="nw">&#34;sinc&#34;</span></code>, <code><span class="nw">window&#61;&#34;hamming&#34;</span></code> | <code><span class="nw">&#34;hamming&#34;</span></code> | <code><span class="nw">c</span></code>osine, <code><span class="nw">w</span></code>elch, <code><span class="nw">b</span></code>lackman, <code><span class="nw">l</span></code>anczos, <code><span class="nw">h</span></code>amming (the first letter); radius 3; outside the image the nearest edge voxel; 3D |
| 6 <code><span class="nw">4</span></code>, then the order | <code><span class="nw">&#34;bspline&#34;</span></code>, <code><span class="nw">order&#61;3</span></code> | <code><span class="nw">3</span></code> | orders 0 to 5 (others are 3); 3D |
| <code><span class="nw">pixeltype</span></code> 0 to 7, after the interpolator's parameters | <code><span class="nw">pixel&#95;type&#61;&#34;char&#34;</span></code>, <code><span class="nw">&#34;uchar&#34;</span></code>, <code><span class="nw">&#34;short&#34;</span></code>, <code><span class="nw">&#34;ushort&#34;</span></code>, <code><span class="nw">&#34;int&#34;</span></code>, <code><span class="nw">&#34;uint&#34;</span></code>, <code><span class="nw">&#34;float&#34;</span></code> (default), <code><span class="nw">&#34;double&#34;</span></code> | <code><span class="nw">&#34;float&#34;</span></code> | the type the image is read as and written in; ANTs reads it as the seventh argument whatever the interpolator ([the seventh argument](repo:docs/api/ants-resample-image.md#the-seventh-argument)) |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code> (or <code><span class="nw">NSLOTS</span></code>, as ITK reads them) | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants ResampleImage ...`); `lx.ants.resample_image` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;resample&#95;image</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `t1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# The 4 mm head to 2 mm, linear; to a size of 20 x 24 x 20 by B-spline.
fine = lx.ants.resample_image("t1w.nii.gz", 2.0)
fine.shape  # -> (80, 96, 80)
coarse = lx.ants.resample_image("t1w.nii.gz", size=[20, 24, 20], interpolation="bspline")
coarse.shape  # -> (20, 24, 20)
```

```bash
larmorx ants ResampleImage 3 t1w.nii.gz t1w_2mm.nii.gz 2
larmorx ants ResampleImage 3 t1w.nii.gz on_grid.nii.gz 20x24x20 1 4
larmorx ants ResampleImage 3 t1w.nii.gz nearest_short.nii.gz 3 0 1 2
larmorx ants ResampleImage 3 t1w.nii.gz sinc.nii.gz 3 0 3 w 3
larmorx ants ResampleImage 3 t1w.nii.gz smooth.nii.gz 2 0 2 1.5x1.5x1.5 2 1
```

## Ports {#ports}

`ResampleImage` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-resample-image](repo:docs/validation/ants-resample-image.md) |

**The replica: status `validated`** against ResampleImage itself (its
[record](repo:docs/validation/ants-resample-image.md), 2026-10-24): 57 cases, 47 outputs compared, all
bit-identical with ANTs' exact header bytes: the eight pixel types, every interpolator (B-spline
orders 0 to 5, Gaussian, windowed sinc), by spacing and by size, in 2, 3 and 4 dimensions, and a
size of 1 (ANTS-29); 8 rejected by both alike. One expected divergence: B-spline, Gaussian and
windowed-sinc interpolation of 2D and 4D images are not supported yet. Compared with ANTs'
defects reproduced (`LARMORX_UPSTREAM_DEFECTS=reproduce`); the record's "D13 fix pass" lists
what larmorx's default changes.

**On the data panel** ([record](repo:docs/validation/ants-resample-image-panel.md), 2026-10-26):
fMRIPrep 25.2.6 never calls `ResampleImage`; on the panel's images (the 82-year-old's FLAIR to 1
mm, linear; the 7 T MP2RAGE to 1 mm, B-spline; a glioma's T2w to 0.8 mm, windowed sinc; the
stroke's lesion mask to a size, nearest): **4 of 4 bit-identical, header bytes included**.

`ResampleImage` has one port, in `pip install larmorx`: **the replica** (`crates/larmorx-ants`,
`crates/larmorx-interp`; Apache-2.0; Rust `larmorx_ants::resample_image`,
`larmorx_ants::resample`, `larmorx_interp`), translated from ANTs 2.6.5 on ITK 5.4.5
(Apache-2.0).

## Evidence {#evidence}

How each of `ResampleImage`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-programs/).

## More in the repository {#more}

The API page [docs/api/ants-resample-image.md](repo:docs/api/ants-resample-image.md) holds what `ResampleImage` shares with the page's other programs:

- [Speed](repo:docs/api/ants-resample-image.md#speed)
- [The seventh argument](repo:docs/api/ants-resample-image.md#the-seventh-argument)
- [Behaviour worth knowing](repo:docs/api/ants-resample-image.md#behaviour-worth-knowing)
- [Upstream defects (D13)](repo:docs/api/ants-resample-image.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/ants-resample-image.md#deliberate-differences)
