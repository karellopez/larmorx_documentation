---
title: "`ImageMath`"
kicker: "Programs · ANTs and ITK"
lede: "`ImageMath` applies one operation to an image (and to a second image or numbers): arithmetic, intensity clipping and scaling, Gaussian filters, binary and grayscale morphology, hole filling, padding, connected components and distance maps."
description: "LARMORX reference for ANTs 2.6.5 `ImageMath`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants ImageMath"
  python: "lx.ants.image_math"
  api: "docs/api/ants-image-math.md"
  evidence: "/evidence/ants-programs/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/image_math/mod.rs: "96fcaac3e2fa5fde"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "035dcd92e164879c"
    docs/api/ants-image-math.md: "4df6eee49b1b5870"
    python/larmorx/ants/image_math.py: "6844b6d286b9f0a8"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

The implemented operations (the others answer "not supported yet"):

| Group | Operations |
|---|---|
| arithmetic | `m`, `+`, `-`, `/`, `^`, `exp`, `max`, `abs`, `addtozero`, `overadd`, `Decision`, `total`, `mean`, `vtotal`, `Neg` |
| intensity | `TruncateImageIntensity`, `Normalize`, `RescaleImage`, `ThresholdAtMean`, `ReplaceVoxelValue` |
| gaussian | `G`, `Laplacian`, `Grad`, `UnsharpMask` |
| morphology | `MD`, `ME`, `MO`, `MC`, `GD`, `GE`, `GO`, `GC`, `FillHoles`, `PadImage` |
| components | `GetLargestComponent`, `D`, `MaurerDistance`, `ExtractContours` |

All of them run in 2, 3 and 4 dimensions, as in ANTs; the Gaussian and morphology operations
work in all of the image's dimensions (a 4D image along time too).

## Command line {#command-line}

```text synopsis
larmorx ants ImageMath <dimension> <output> <operation> <operands...>
```

Everything after `larmorx ants ImageMath` is the original's command line: the arguments of ANTs 2.6.5's `ImageMath`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants ImageMath ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

## Python {#python}

```python
lx.ants.image_math(
    operation: str,
    *operands: Any,
    dimension: int = 3,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
) -> Image
```

Where `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

Run ImageMath `operation` on `operands`, as `ImageMath <dimension> <output> <operation> <operands...>` does.

Runs `ImageMath <dimension> <output> <operation> <operands...>` with images held in memory:
`lx.Image` objects, nibabel images and `(array, affine)` pairs are passed without files;
paths, numbers and strings are passed as on the command line (numbers as their shortest
round-trip text). Returns the image the operation writes, in the type and geometry ANTs
gives it. Raises `lx.ants.ImageMathError` with the program's messages when it fails or writes
nothing. `lx.ants.image_math_operations()` lists the implemented operations.

In-memory images are placed by their affine (the spatial axes) and their header's
repetition time (a fourth axis; spacing 1 without a header); files are read as ITK reads
them. Each operation also has a typed function, `lx.ants.truncate_image_intensity` and the
others the API page lists under "Typed functions".

```python
import larmorx as lx

# fMRIPrep's intensity clipping of the T1w before registration
t1 = lx.ants.truncate_image_intensity("sub-01_T1w.nii.gz", 0.01, 0.999, 256)

# The command line, on in-memory images (exactly the command-line code)
t1 = lx.ants.image_math("TruncateImageIntensity", "sub-01_T1w.nii.gz", 0.01, 0.999, 256)
both = lx.ants.add_to_zero(wm_mask, gm_mask)

# The Laplacian feature channel of fMRIPrep's brain extraction (ImageMath 3 out Laplacian in 1.5 1)
lap = lx.ants.laplacian(t1, 1.5, normalize=True)

# sMRIPrep's mask clean-up steps (ImageMath MD 2, ME 10, FillHoles 2, PadImage 10)
mask = lx.ants.morphological_dilate("brain_mask.nii.gz", 2)
csf = lx.ants.morphological_erode(csf_mask, 10)
filled = lx.ants.fill_holes(gm_mask, 2)
padded = lx.ants.pad_image(mask, 10)
largest = lx.ants.largest_component(mask)
dist = lx.ants.maurer_distance(mask)  # signed, mm, negative inside
```

Its result, `Image`, holds a voxel array placed in world space by an affine.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">data</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">affine</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">header</span></code> | <code><span class="nw">NiftiHeader</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">Implementation</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `ImageMath` accepts (`crates/larmorx-ants/src/cli/image_math/mod.rs`) and the arguments of `lx.ants.image_math` (`python/larmorx/ants/image_math.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs argument (positional) | Python | Default | Notes |
|---|---|---|---|
| 1 <code><span class="nw">ImageDimension</span></code> (2, 3, 4) | <code><span class="nw">dimension&#61;3</span></code> | <code><span class="nw">3</span></code> | a path is read in that many dimensions |
| 2 <code><span class="nw">outputImage</span></code> | the result |  | in the type and geometry ANTs gives it |
| 3 <code><span class="nw">operation</span></code> | <code><span class="nw">operation</span></code> |  | ImageMath's name, case-sensitive (the implemented operations are listed above the Python call) |
| 4 and after: the operands | <code><span class="nw">operands</span></code> |  | images (paths, <code><span class="nw">lx&#46;Image</span></code>, nibabel images, <code><span class="nw">&#40;array&#44;</span> <span class="nw">affine&#41;</span></code>), numbers and strings, in the operation's order |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code> (or <code><span class="nw">NSLOTS</span></code>, as ITK reads them) | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants ImageMath ...`); `lx.ants.image_math` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;image&#95;math</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `t1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `mask.nii.gz` (the synthetic head's brain as a mask (1 inside, 0 outside)). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# fMRIPrep's clipping of the T1w's intensities, through the command line's code.
clipped = lx.ants.image_math("TruncateImageIntensity", "t1w.nii.gz", 0.01, 0.999, 256)
clipped.shape  # -> (40, 48, 40)
# sMRIPrep's dilation of a mask by 2 voxels, through its typed function.
dilated = lx.ants.morphological_dilate("mask.nii.gz", 2)
dilated.data.dtype  # -> dtype('float32')
```

```bash
larmorx ants ImageMath 3 clipped.nii.gz TruncateImageIntensity t1w.nii.gz 0.01 0.999 256
larmorx ants ImageMath 3 laplacian.nii.gz Laplacian t1w.nii.gz 1.5 1
larmorx ants ImageMath 3 dilated.nii.gz MD mask.nii.gz 2
larmorx ants ImageMath 3 filled.nii.gz FillHoles mask.nii.gz 2
```

## Ports {#ports}

`ImageMath` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-image-math](repo:docs/validation/ants-image-math.md) |

**The replica: status `validated`** for the implemented operations, against ImageMath itself
(its [record](repo:docs/validation/ants-image-math.md), 2026-10-24): 334 cases, 308 outputs compared,
303 bit-identical, 24 rejected by both alike; every output has ANTs' exact header bytes. Of the 5
others, 3 are `^`, where ANTs calls glibc's `powf`, which is not correctly rounded; larmorx's is,
so up to 35 of 35,840 voxels differ by one ulp ([why](repo:docs/findings/platform-math.md#powf)); 2 are
grayscale morphology on an image made to hold `-0.0` next to `+0.0`, where only the sign of a
zero result differs ([why](repo:docs/findings/ants-morphology.md#grayscale-morphology)). Every Gaussian
case (`G`, `Laplacian`, `Grad`, `UnsharpMask`; 47 compared, in 2, 3 and 4 dimensions, fMRIPrep's
`Laplacian 1.5 1` on real T1w, boldref and template images included) is bit-identical, and so is
every other morphology case (100 compared: `MD`, `ME`, `MO`, `MC`, `GD`, `GE`, `GO`, `GC`,
`FillHoles`, `PadImage` in 2, 3 and 4 dimensions, sMRIPrep's `MD 2/5`, `ME 2/10`, `FillHoles 2`
and `PadImage ±10` on real masks included), and every component and distance-map case (61
compared: `GetLargestComponent`, `D`, `MaurerDistance`, `ExtractContours`, `ThresholdAtMean`,
`ReplaceVoxelValue`, in 2, 3 and 4 dimensions, on real masks and probability maps too).
Compared with ANTs' defects reproduced (`LARMORX_UPSTREAM_DEFECTS=reproduce`); the record's "D13
fix pass" lists what larmorx's default changes. One more case, `FillHoles 0.5` with a hole on the
first slice, compares everything but the values, which ANTs takes from memory outside the image
(ANTS-19).

**On the data panel** ([record](repo:docs/validation/ants-image-math-panel.md), 2026-10-27): every
ImageMath node of the fourteen finished fMRIPrep oracle runs (378 nodes, 365 distinct calls:
sMRIPrep's brain extraction and template steps, the BOLD references' and field maps' masks),
each replayed from its node with its inputs, and nine calls on the panel's images (truncation of
the 7 T MP2RAGE, a FLAIR and a 1.5 T float T1w, Laplacians of a glioma's and an older adult's
T2w, the stroke lesion mask's components, morphology and holes, a 600-volume multiband-8 series
times a scalar): **374 of 374 bit-identical, header bytes included**.

`ImageMath` has one port, in `pip install larmorx`: **the replica** (`crates/larmorx-ants`,
`crates/larmorx-image`; Apache-2.0; Rust `larmorx_ants::image_math` (operations),
`larmorx_ants::cli::image_math` (the dispatcher), `larmorx_image` (ITK filters)), translated
from ANTs 2.6.5 on ITK 5.4.5 (Apache-2.0).

## Evidence {#evidence}

How each of `ImageMath`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-programs/).

## More in the repository {#more}

The API page [docs/api/ants-image-math.md](repo:docs/api/ants-image-math.md) holds what `ImageMath` shares with the page's other programs:

- [Speed](repo:docs/api/ants-image-math.md#speed)
- [Typed functions](repo:docs/api/ants-image-math.md#typed-functions)
- [Command-line behaviour (as in ANTs)](repo:docs/api/ants-image-math.md#command-line-behaviour-as-in-ants)
- [Behaviour worth knowing](repo:docs/api/ants-image-math.md#behaviour-worth-knowing)
- [Upstream defects (D13)](repo:docs/api/ants-image-math.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/ants-image-math.md#deliberate-differences)
