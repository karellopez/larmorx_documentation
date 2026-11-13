---
title: "`DenoiseImage`"
kicker: "Programs · ANTs and ITK"
lede: "`DenoiseImage` denoises an image by adaptive non-local means."
description: "LARMORX reference for ANTs 2.6.5 `DenoiseImage`: its command line, its Python call, every option, tested examples and its ports."
template: reference
reference:
  group: ants
  original: "ANTs 2.6.5"
  software: "ANTs"
  command: "larmorx ants DenoiseImage"
  python: "lx.ants.denoise_image"
  api: "docs/api/ants-denoise.md"
  evidence: "/evidence/ants-denoise/"
  ports:
    - {kind: replica, name: "replica", package: larmorx, licence: "Apache-2.0", status: "validated"}
  sources:
    CHANGELOG.md: "546736ae45f1a3f5"
    crates/larmorx-ants/src/cli/denoise_image.rs: "261344b4db29b096"
    crates/larmorx-cli/src/replica.rs: "bdcff4968024a104"
    crates/larmorx-core/src/cli.rs: "01fa0015abc1a111"
    crates/larmorx-core/src/defects.rs: "91be42d24bb3ba2b"
    docs/api/ants-denoise.md: "c576e5bfacbda98c"
    python/larmorx/ants/denoise.py: "87af5cf9ba5c5aa4"
    validation/tools.toml: "f873f72ba8c4985c"
---

## What it does {#what-it-does}

The method is Manjón et al.'s
(*Adaptive non-local means denoising of MR images with spatially varying noise levels*, JMRI
31:192-203, 2010); sMRIPrep runs it on every T1w (`-n Rician`, ANTs' other defaults).

## Command line {#command-line}

```text synopsis
larmorx ants DenoiseImage [-d 2/3/4] -i input [-n Rician/(Gaussian)] [-x mask] [-s (1)/2/3/...]
                 [-p 1|1x1x1] [-r 2|2x2x2] [-o corrected | [corrected,<noise>]] [-v (0)/1]
```

Everything after `larmorx ants DenoiseImage` is the original's command line: the arguments of ANTs 2.6.5's `DenoiseImage`, as ANTs takes them. LARMORX's own options stand between `larmorx` and the family `ants`, so they never meet the original's ([below](#larmorx-options)):

```text synopsis
larmorx
        [--n-threads N]
        [--implementation auto|replica|clean-room]
        [--upstream-defects fix|reproduce]
        ants DenoiseImage ...
```

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

<details class="usage"><summary><code>DenoiseImage</code>'s usage text, as the replica prints it</summary>

```text
COMMAND:
     DenoiseImage (larmorx port of ANTs v2.6.5)
          Denoise an image using a spatially adaptive filter originally described in J. V.
          Manjon, P. Coupe, Luis Marti-Bonmati, D. L. Collins, and M. Robles. Adaptive
          Non-Local Means Denoising of MR Images With Spatially Varying Noise Levels, Journal
          of Magnetic Resonance Imaging, 31:192-203, June 2010.

OPTIONS:
     -d, --image-dimensionality 2/3/4
     -i, --input-image inputImageFilename
     -n, --noise-model Rician/(Gaussian)
     -x, --mask-image maskImageFilename
     -s, --shrink-factor (1)/2/3/...
     -p, --patch-radius 1
                        1x1x1
     -r, --search-radius 2
                         2x2x2
     -o, --output correctedImage
                  [correctedImage,<noiseImage>]
     --version
     -v, --verbose (0)/1
     -h
     --help
```

</details>

## Python {#python}

```python
lx.ants.denoise_image(
    image: Any,
    noise_model: Literal["Rician", "Gaussian"] = "Rician",
    mask: Any = None,
    shrink_factor: int = 1,
    patch_radius: int | Sequence[int] = 1,
    search_radius: int | Sequence[int] = 2,
    *,
    dimension: int | None = None,
    n_threads: int = 1,
    upstream_defects: UpstreamDefectsName = "fix",
) -> DenoiseResult
```

Where `UpstreamDefectsName` is one of `"fix"`, `"reproduce"`.

`DenoiseImage -d D -i image -n model [-x mask] -s shrink -p patch -r search -o [denoised,noise]`: adaptive non-local means (Manjón et al., JMRI 2010).

Returns a `DenoiseResult`: `denoised` and `noise`, float32 images on the input's grid (the noise
is always returned). `image` is a path, an `lx.Image`, a nibabel image or `(array, affine)`,
read as `float`.

```python
import larmorx as lx

# sMRIPrep's call: Rician noise model, patch radius 1, search radius 2, no shrinking
res = lx.ants.denoise_image("sub-01_T1w.nii.gz", n_threads=8)
res.denoised.to_filename("sub-01_desc-denoised_T1w.nii.gz")
noise = res.noise                       # image − denoised

# the Gaussian model, only inside a mask, larger patches
res = lx.ants.denoise_image(t1w, "Gaussian", mask=brain_mask, patch_radius=2)
```

Its result, `DenoiseResult`, holds the denoised image and the noise removed from it (`image - denoised`, as ANTs computes it: the noise is estimated at the filter's resolution and resampled onto the image's grid, then subtracted).

| Field | Type | What it holds |
|---|---|---|
| <code><span class="nw">denoised</span></code> | <code><span class="nw">Image</span></code> |  |
| <code><span class="nw">noise</span></code> | <code><span class="nw">Image</span></code> |  |

## Options {#options}

Each row joins an option of the original's command line with the Python argument that does the same. The rows are checked against the code at every test run: the options `DenoiseImage` accepts (`crates/larmorx-ants/src/cli/denoise_image.rs`) and the arguments of `lx.ants.denoise_image` (`python/larmorx/ants/denoise.py`), whose defaults and descriptions are taken from it. Under each option, in grey, ANTs's own help for it.

| ANTs option | Python | Default | Notes |
|---|---|---|---|
| <code><span class="nw">&#45;d</span> <span class="nw">2&#47;3&#47;4</span></code>, <code><span class="nw">&#45;&#45;image&#45;dimensionality</span></code> | <code><span class="nw">dimension</span></code> | <code><span class="nw">None</span></code> | default: the image's; a 4D file read with <code><span class="nw">&#45;d</span> <span class="nw">3</span></code> gives its first volume; in 4D, patches and search boxes extend along time too |
| <code><span class="nw">&#45;i</span> <span class="nw">image</span></code>, <code><span class="nw">&#45;&#45;input&#45;image</span></code> | <code><span class="nw">image</span></code> |  | path, <code><span class="nw">lx&#46;Image</span></code>, nibabel image or <code><span class="nw">&#40;array&#44;</span> <span class="nw">affine&#41;</span></code>; read as <code><span class="nw">float</span></code> |
| <code><span class="nw">&#45;n</span> <span class="nw">Rician&#47;&#40;Gaussian&#41;</span></code>, <code><span class="nw">&#45;&#45;noise&#45;model</span></code> | <code><span class="nw">noise&#95;model&#61;&#34;Rician&#34;</span></code> | <code><span class="nw">&#34;Rician&#34;</span></code> | **different default**: the command line's is Gaussian, Python's is Rician (sMRIPrep's choice). Case does not matter |
| <code><span class="nw">&#45;x</span> <span class="nw">mask</span></code>, <code><span class="nw">&#45;&#45;mask&#45;image</span></code> | <code><span class="nw">mask</span></code> | <code><span class="nw">None</span></code> | read as <code><span class="nw">unsigned</span> <span class="nw">char</span></code> (0.4 → 0; values beyond 0 to 255 clamped, ANTS-06 in [Upstream defects](repo:docs/api/ants-denoise.md#upstream-defects-d13)); only voxels where it is not 0 are patch centres. Must be on the grid the filter runs on (the shrunk grid with <code><span class="nw">&#45;s</span></code> above 1) |
| <code><span class="nw">&#45;s</span> <span class="nw">1</span></code>, <code><span class="nw">&#45;&#45;shrink&#45;factor</span></code> | <code><span class="nw">shrink&#95;factor&#61;1</span></code> | <code><span class="nw">1</span></code> | <code><span class="nw">ShrinkImageFilter</span></code> along every axis (time too); 0 acts as 1. The noise is resampled linearly onto the full grid |
| <code><span class="nw">&#45;p</span> <span class="nw">1</span></code> / <code><span class="nw">&#45;p</span> <span class="nw">1x1x1</span></code>, <code><span class="nw">&#45;&#45;patch&#45;radius</span></code> | <code><span class="nw">patch&#95;radius&#61;1</span></code> / <code><span class="nw">&#40;1&#44;</span> <span class="nw">1&#44;</span> <span class="nw">1&#41;</span></code> | <code><span class="nw">1</span></code> | one value for every axis or one per axis |
| <code><span class="nw">&#45;r</span> <span class="nw">2</span></code> / <code><span class="nw">&#45;r</span> <span class="nw">2x2x2</span></code>, <code><span class="nw">&#45;&#45;search&#45;radius</span></code> | <code><span class="nw">search&#95;radius&#61;2</span></code> / <code><span class="nw">&#40;2&#44;</span> <span class="nw">2&#44;</span> <span class="nw">2&#41;</span></code> | <code><span class="nw">2</span></code> | one value for every axis or one per axis |
| <code><span class="nw">&#45;o</span> <span class="nw">out</span></code> / <code><span class="nw">&#45;o</span> <span class="nw">&#91;out&#44;noise&#93;</span></code>, <code><span class="nw">&#45;&#45;output</span></code> | the result |  | its <code><span class="nw">denoised</span></code> and <code><span class="nw">noise</span></code>, float32 images on the input's grid |
| <code><span class="nw">&#45;v</span> <span class="nw">1</span></code>, <code><span class="nw">&#45;&#45;verbose</span></code> | (command line only) |  | ANTs' progress characters and the elapsed time |
| <code><span class="nw">&#45;&#45;version</span></code> | (command line only) |  | the version line |
| <code><span class="nw">&#45;h</span></code>, <code><span class="nw">&#45;&#45;help</span></code> | (command line only) |  | ANTs' short and long help |
| <code><span class="nw">ITK&#95;GLOBAL&#95;DEFAULT&#95;NUMBER&#95;OF&#95;THREADS</span></code> (or <code><span class="nw">NSLOTS</span></code>, as ITK reads them) | <code><span class="nw">n&#95;threads</span></code> | <code><span class="nw">1</span></code> | **ANTs' result depends on it; larmorx's does not**: it always gives ANTs' one-thread result |
| <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> | <code><span class="nw">upstream&#95;defects</span></code> | <code><span class="nw">&#34;fix&#34;</span></code> | <code><span class="nw">fix</span></code> (default) or <code><span class="nw">reproduce</span></code> ([Upstream defects](repo:docs/api/ants-denoise.md#upstream-defects-d13)) |

### LARMORX's own options {#larmorx-options}

**From the next release.** In 0.1.0rc1, set the variables instead: `OMP_NUM_THREADS`, `LARMORX_IMPLEMENTATION` (`original` for the clean room) and `LARMORX_UPSTREAM_DEFECTS`.

They stand between `larmorx` and `ants` on the command line (`larmorx --n-threads 4 ants DenoiseImage ...`); `lx.ants.denoise_image` takes `n_threads` and `upstream_defects` as arguments, and the other is the command line's only. Each one given wins over its environment variable, which keeps working.

| Command line, then Python | What it does |
|---|---|
| <code><span class="nw">&#45;&#45;n&#45;threads</span></code> <code><span class="nw">N</span></code><br><code><span class="nw">n&#95;threads&#61;1</span></code> | Default: every logical CPU on the command line (<code><span class="nw">0</span></code>), <code><span class="nw">1</span></code> in Python. The variable <code><span class="nw">OMP&#95;NUM&#95;THREADS</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;implementation</span></code> <code><span class="nw">auto&#124;replica&#124;clean&#45;room</span></code><br>(no Python argument) | The command line's only: <code><span class="nw">lx&#46;ants&#46;denoise&#95;image</span></code> takes no <code><span class="nw">implementation</span></code>. The variable <code><span class="nw">LARMORX&#95;IMPLEMENTATION</span></code> in 0.1.0rc1. |
| <code><span class="nw">&#45;&#45;upstream&#45;defects</span></code> <code><span class="nw">fix&#124;reproduce</span></code><br><code><span class="nw">upstream&#95;defects&#61;&#34;fix&#34;</span></code> | The variable <code><span class="nw">LARMORX&#95;UPSTREAM&#95;DEFECTS</span></code> in 0.1.0rc1. |

## Examples {#examples}

The tests run every example below ([`validation/tests/test_reference.py`](repo:validation/tests/test_reference.py)), each section in a new folder where these inputs are made first: `t1w.nii.gz` (a synthetic head of 40 × 48 × 40 voxels of 4 mm). The command lines run as `python -m larmorx`.

```python
import larmorx as lx

# sMRIPrep's call: the Rician noise model, ANTs' other defaults.
res = lx.ants.denoise_image("t1w.nii.gz")
res.denoised.data.dtype  # -> dtype('float32')
```

```bash
larmorx ants DenoiseImage -d 3 -i t1w.nii.gz -n Rician -s 1 -o [ denoised.nii.gz, noise.nii.gz ]
```

## Ports {#ports}

`DenoiseImage` has one port: a replica.

| Port | Package | Licence | Status | Records |
|---|---|---|---|---|
| replica | <code><span class="nw">larmorx</span></code> (built in) | Apache-2.0 | validated | [ants-denoise](repo:docs/validation/ants-denoise.md) |

**The replica: status `validated`** against DenoiseImage itself (its
[record](repo:docs/validation/ants-denoise.md), 2026-10-24, standard tier: 51 cases, 42 pass, 9
rejected by both alike; 40 compared cases, 52 outputs), on sMRIPrep's command line on real T1w
images and on every option, in 2, 3 and 4 dimensions:
- against the **unmodified ANTs 2.6.5 binary** at one thread: 7 of 40 cases (9 of 52 outputs)
  bit-identical. In the others, glibc's `expf` (or `exp`), which is not always correctly
  rounded, changes a few voxels by a few float units: on sMRIPrep's command, 5,522 of
  5,898,240 voxels of ds000005's T1w by at most 2.0e-4 and 5,389 of 11,534,336 of ds000210's
  by at most 2.1e-3; 1 − NCC at most 2.2e-13 in every case, and every difference at most
  2.2e-4 of ANTs' own difference between thread counts;
- against the **same binary run with glibc's `expf`, `exp` (and `logf`, `log`, `sin`, `cos`,
  `sincos`) replaced by CORE-MATH's correctly rounded ones** (`LD_PRELOAD`,
  `scripts/build_crmath_preload.sh`), which is the arithmetic larmorx uses: **52 of 52 outputs
  bit-identical**. ANTs' own code is not changed; only those C-library functions are.
- **ANTs' own result depends on its thread count**, far more than on the C library: with 2
  threads a fifth of the voxels of a T1w change, by up to 97; with 8 or 12 the result also
  changes from run to run. larmorx always gives ANTs' one-thread result.

**On the data panel** ([record](repo:docs/validation/ants-denoise-panel.md), 2026-10-26): sMRIPrep's
command on every T1w of the fourteen finished oracle runs (17 calls: the 3.5-year-old, the
glioma, the stroke, strong motion, 1.5 T and 7 T among them, and the runs with several T1w), each
replayed from its node with the node's inputs, and four images fMRIPrep never denoises (the 7 T
MP2RAGE, the 82-year-old's FLAIR, a child's T2w with `-n Rician`, the 1.5 T T1w as float with
`-n Gaussian`): **21 of 21 bit-identical to ANTs with CORE-MATH**; against the unmodified ANTs,
glibc's `expf` changes voxels in all 21, by at most 0.0015 of ANTs' own difference between one
thread and two or three, 1 − NCC below 2e-17.

`DenoiseImage` has one port, in `pip install larmorx`: **the replica** (`crates/larmorx-ants`,
`crates/larmorx-image`; Apache-2.0; Rust `larmorx_ants::denoise_image`,
`larmorx_image::adaptive_denoising`), translated from ANTs 2.6.5's `DenoiseImage` on the
`AdaptiveNonLocalMeansDenoisingImageFilter` of ITK 5.4.5's remote module AdaptiveDenoising
(commit `24825c8d`, Apache-2.0). Its result does not depend on the thread count: it is always
ANTs' one-thread result.

## Evidence {#evidence}

How each of `DenoiseImage`'s ports was measured against ANTs, case by case: [its evidence](/evidence/ants-denoise/).

## More in the repository {#more}

The API page [docs/api/ants-denoise.md](repo:docs/api/ants-denoise.md) holds what `DenoiseImage` shares with the page's other programs:

- [Speed](repo:docs/api/ants-denoise.md#speed)
- [Behaviour worth knowing](repo:docs/api/ants-denoise.md#behaviour-worth-knowing)
- [Upstream defects (D13)](repo:docs/api/ants-denoise.md#upstream-defects-d13)
- [Deliberate differences](repo:docs/api/ants-denoise.md#deliberate-differences)
- [Rust](repo:docs/api/ants-denoise.md#rust)
