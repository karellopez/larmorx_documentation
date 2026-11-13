---
title: "`ThresholdImage`"
kicker: "Programs · ANTs and ITK"
lede: "`ThresholdImage` sets the voxels between two bounds to one value and the others to another, or labels an image's classes by Otsu's thresholds."
description: "LARMORX reference for ANTs 2.6.5 `ThresholdImage`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants ThresholdImage"
  python: "lx.ants.threshold_image"
  api: "docs/api/ants-threshold-image.md"
  evidence: "/evidence/ants-programs/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/threshold_image.rs: "69402d431da56215"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "24c23485c8957683"
    docs/api/ants-threshold-image.md: "90b2e3a5d56fc99e"
    python/larmorx/ants/threshold.py: "8eb31db682525d28"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

sMRIPrep's brain extraction, which fMRIPrep runs,
binarises a brain probability map with it (`0.5 1 1 0`).

## Command line {#command-line}

```text synopsis
larmorx ants ThresholdImage ImageDimension ImageIn.ext outImage.ext threshlo threshhi <insideValue> <outsideValue>
larmorx ants ThresholdImage ImageDimension ImageIn.ext outImage.ext Otsu NumberofThresholds <maskImage.ext>
larmorx ants ThresholdImage ImageDimension ImageIn.ext outImage.ext Kmeans NumberofThresholds <maskImage.ext>
```

Everything after `larmorx ants ThresholdImage` is the original's command line: the arguments of ANTs 2.6.5's `ThresholdImage`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants ThresholdImage ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>ThresholdImage</code>'s usage text, as the replica prints it</summary>

```text
Usage: ThresholdImage   ImageDimension ImageIn.ext outImage.ext  threshlo threshhi <insideValue> <outsideValue>
   ImageDimension ImageIn.ext outImage.ext  Otsu NumberofThresholds <maskImage.ext>
   ImageDimension ImageIn.ext outImage.ext  Kmeans NumberofThresholds <maskImage.ext> (not supported by larmorx yet)
 Inclusive thresholds
```

</details>

## Python {#python}

```python
lx.ants.threshold_image(
    image: Any,
    lower: float,
    upper: float,
    inside: float = 1.0,
    outside: float = 0.0,
    *,
    n_threads: int = 1,
) -> Image
```

`ThresholdImage d in out lower upper inside outside`: `inside` where `lower <= v <= upper` (bounds compared in float32), else `outside`. A float32 image, as ANTs writes it.

Returns a float32 `lx.Image`: `inside` where `lower <= v <= upper` (the bounds compared in
float32), else `outside`; `lower > upper` raises `ValueError` (ANTs aborts). Otsu's mode is a
function of its own, `lx.ants.otsu_threshold(image, n_thresholds=1, *, mask=None, n_threads=1,
upstream_defects="fix")`, which returns `OtsuResult(image, thresholds)`, the thresholds being
the upper bounds of the chosen histogram bins.

```python
import larmorx as lx

# fMRIPrep binarises a brain probability map: 1 where 0.5 <= p <= 1, else 0
mask = lx.ants.threshold_image("prob.nii.gz", 0.5, 1.0)

# Otsu: three classes inside a brain mask (labels 1..3, 0 outside)
r = lx.ants.otsu_threshold(t1w, 2, mask=brain_mask)
r.image, r.thresholds
```

Its result, `Image`, holds a voxel array placed in world space by an affine.

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">data</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">affine</span></code> | <code><span class="nw">np&#46;ndarray</span></code> |  |
| <code><span class="nw">header</span></code> | <code><span class="nw">NiftiHeader</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |
| <code><span class="nw">implementation</span></code> | <code><span class="nw">Implementation</span> <span class="nw">&#124;</span> <span class="nw">None</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `ThresholdImage` accepts (`crates/larmorx-ants/src/cli/threshold_image.rs`) and the arguments of `lx.ants.threshold_image` (`python/larmorx/ants/threshold.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs argument (positional) | Python | Default | Notes |
|---|---|---|---|
| 1 <code><span class="nw">ImageDimension</span></code> | – |  | 2, 3, 4; Python takes any array shape |
| 2 <code><span class="nw">ImageIn&#46;ext</span></code> | <code><span class="nw">image</span></code> |  | path, <code><span class="nw">lx&#46;Image</span></code>, nibabel image or <code><span class="nw">&#40;array&#44;</span> <span class="nw">affine&#41;</span></code> |
| 3 <code><span class="nw">outImage&#46;ext</span></code> | the result |  | float32, as ANTs writes it |
| 4 <code><span class="nw">threshlo</span></code> | <code><span class="nw">lower</span></code> |  | inclusive; read with <code><span class="nw">atof</span></code>, then compared in float |
| 5 <code><span class="nw">threshhi</span></code> | <code><span class="nw">upper</span></code> |  | inclusive |
| 6 <code><span class="nw">insideValue</span></code> | <code><span class="nw">inside</span></code> | <code><span class="nw">1&#46;0</span></code> | default 1 |
| 7 <code><span class="nw">outsideValue</span></code> | <code><span class="nw">outside</span></code> | <code><span class="nw">0&#46;0</span></code> | default 0 |
| 4 <code><span class="nw">Otsu</span></code>, 5 <code><span class="nw">NumberofThresholds</span></code> | <code><span class="nw">lx&#46;ants&#46;otsu&#95;threshold&#40;image&#44;</span> <span class="nw">n&#95;thresholds&#41;</span></code> |  | ITK's <code><span class="nw">OtsuMultipleThresholdsImageFilter</span></code>, 128 bins, labels <code><span class="nw">0&#46;&#46;n</span></code> |
| 6 <code><span class="nw">maskImage&#46;ext</span></code> (with <code><span class="nw">Otsu</span></code>) | <code><span class="nw">lx&#46;ants&#46;otsu&#95;threshold&#40;&#46;&#46;&#46;&#44;</span> <span class="nw">mask&#61;&#46;&#46;&#46;&#41;</span></code> |  | ANTs' own code: region = mask value 1 (as <code><span class="nw">int</span></code>), 200 bins, labels <code><span class="nw">1&#46;&#46;n&#43;1</span></code> inside, 0 outside; the output takes the mask's geometry |
| 4 <code><span class="nw">Kmeans</span></code>, 5 <code><span class="nw">NumberofThresholds</span></code>, 6 <code><span class="nw">maskImage&#46;ext</span></code> | – |  | not supported yet |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code> (or <code><span class="nw">NSLOTS</span></code>, as ITK reads them) | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | the result does not depend on it |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants ThresholdImage ...`); `lx.ants.threshold_image` takes `n_threads` as an argument, and the others are the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;threshold&#95;image</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;threshold&#95;image</span></code> takes no <code><span class="nw">upstream&#95;defects</span></code>. The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `prob.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm), `mask.nii.gz` (the synthetic head's brain as a mask (1 inside, 0 outside)). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# 1 where 300 <= v <= 700 (the head's brain and skull), else 0.
inside = lx.ants.threshold_image("prob.nii.gz", 300.0, 700.0)
sorted(set(inside.data.ravel().tolist()))  # -> [0.0, 1.0]
# Otsu's single threshold inside the mask: labels 1 and 2 there, 0 outside.
r = lx.ants.otsu_threshold("prob.nii.gz", 1, mask="mask.nii.gz")
r.image.data.dtype  # -> dtype('float32')
```

```bash
larmorx ants ThresholdImage 3 prob.nii.gz binary.nii.gz 300 700 1 0
larmorx ants ThresholdImage 3 prob.nii.gz otsu.nii.gz Otsu 1 mask.nii.gz
```

## Ports {#ports}

`ThresholdImage` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-threshold-image](repo:docs/validation/ants-threshold-image.md) |

**The replica: status `validated`** against ThresholdImage itself (its
[record](repo:docs/validation/ants-threshold-image.md), 2026-10-12): 41 cases, 35 compared, 5 rejected
by both alike, 1 expected divergence (`Kmeans`, not supported yet); every compared case
bit-identical, with ANTs' exact header bytes. Compared with ANTs' defects reproduced
(`LARMORX_UPSTREAM_DEFECTS=reproduce`); the record's "D13 fix pass" lists what larmorx's default
changes.

**On the data panel** ([record](repo:docs/validation/ants-threshold-image-panel.md), 2026-10-26):
sMRIPrep's `ThresholdImage` in the brain extraction of all fourteen finished oracle runs, each
replayed from its node with its inputs, and four calls fMRIPrep never makes (Otsu with 4, 3 and 2
thresholds on the 7 T MP2RAGE, the 82-year-old's FLAIR and the 1.5 T T1w as float; a range on the
stroke's lesion mask): **18 of 18 bit-identical, header bytes included**.

`ThresholdImage` has one port, in `pip install larmorx`: **the replica** (`crates/larmorx-ants`,
`crates/larmorx-image`; Apache-2.0; Rust `larmorx_ants::threshold_image`,
`larmorx_image::threshold`), translated from ANTs 2.6.5 on ITK 5.4.5 (Apache-2.0).

## Evidence {#evidence}

How each of `ThresholdImage`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-programs/).

## More in the repository {#more}

The API page [docs/api/ants-threshold-image.md](repo:docs/api/ants-threshold-image.md) holds what `ThresholdImage` shares with the page's other programs:

- [Speed](repo:docs/api/ants-threshold-image.md#speed)
- [Behaviour worth knowing](repo:docs/api/ants-threshold-image.md#behaviour-worth-knowing)
- [Upstream defects (D13)](repo:docs/api/ants-threshold-image.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/ants-threshold-image.md#deliberate-differences)
